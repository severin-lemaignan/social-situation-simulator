#! python3

import sys
import time
import os
import argparse

# for video generation
import cv2
import glob
import numpy as np

try:
    import rospy
    from std_msgs.msg import String

    HAS_ROS = True
except ImportError:
    HAS_ROS = False

# allow QML to access local file for read/save simulations
os.environ["QML_XHR_ALLOW_FILE_READ"] = "1"
os.environ["QML_XHR_ALLOW_FILE_WRITE"] = "1"

from pathlib import Path
from PySide6.QtQuick import QQuickView
from PySide6.QtCore import (
    Property,
    Signal,
    Slot,
    QObject,
    QRegularExpression,
)
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QmlElement

import json

from generate_description import describe
import minify

# To be used on the @QmlElement decorator
# (QML_IMPORT_MINOR_VERSION is optional)
QML_IMPORT_NAME = "io.qt.textproperties"
QML_IMPORT_MAJOR_VERSION = 1

agents = {}


@QmlElement
class Bridge(QObject):

    sceneRefresh = Signal(str, arguments=["frame"])
    record = Signal(
        int, int, str, str, arguments=["start", "end", "seen_by", "filename"]
    )

    def __init__(self):
        super().__init__()

    #        self._scene = {}
    #
    #    @Slot(QObject)
    #    def exportScene(self, scene):
    #        agents = scene.findChildren(QObject, QRegularExpression("agent_.*"))
    #
    #        scene = {"agents": {}}
    #
    #        for a in agents:
    #
    #            scene["agents"][a.property("name")] = (
    #                a.property("x_m"),
    #                a.property("y_m"),
    #                a.property("gaze_direction"),
    #            )
    #
    #        print(describe(scene))
    #        self._scene = json.dumps(scene)
    #        self._scene_changed.emit()
    #        print(self._scene)
    #

    @Slot(str, result=str)
    def decode(self, base64_desc):

        try:
            frame = minify.decode(base64_desc)
            return json.dumps(frame)
        except Exception as e:
            return ""

    @Slot()
    def setScene(self, frame):
        self.sceneRefresh.emit(json.dumps(frame))

    def alpha_blend_with_mask(
        self, foreground, background, mask
    ):  # modified func from link
        # Convert uint8 to float
        foreground = foreground.astype(float)
        background = background.astype(float)

        # Normalize the mask mask to keep intensity between 0 and 1
        mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        mask = mask.astype(float) / 255

        # Multiply the foreground with the mask matte
        foreground = cv2.multiply(mask, foreground)

        # Multiply the background with ( 1 - mask )
        background = cv2.multiply(1.0 - mask, background)

        # Add the masked foreground and background.
        return cv2.add(foreground, background).astype(np.uint8)

    @Slot()
    def start_recording(self, start, end, seen_by, name):

        path = f"imgs/{name}"  # frame idx + extension will be added by QML
        self.record.emit(start, end, seen_by, path)

        print("Waiting for rendering...")
        t = 0
        while t < end - start + 1:
            time.sleep(0.1)
            t += 0.1
            sys.stdout.write(".")
            sys.stdout.flush()
        print(f"\nSaving to {path}.mp4...")

        frames = glob.glob(path + "*.png")
        h, w = cv2.imread(frames[0]).shape[:2]

        out = cv2.VideoWriter(
            path + ".mp4", cv2.VideoWriter_fourcc(*"mp4v"), 15, (w, h)
        )

        for f in sorted(frames):
            img = cv2.imread(f, cv2.IMREAD_UNCHANGED)
            img = self.alpha_blend_with_mask(
                img[..., :3], np.ones_like(img[..., :3]) * 255, img[..., 3]
            )
            out.write(img)
            os.remove(f)
        out.release()
        print("Done! Video ready")

    @Slot(str)
    def describe(self, json_situation):
        situation = {float(k): v for k, v in json.loads(json_situation).items()}

        timestamps = sorted(situation.keys())

        print(timestamps)
        print(situation)
        for ts in timestamps:
            print("At %ss:" % ts)
            desc = describe(situation[ts], normalise_names=False)
            print(desc)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Social situation simulator")

    if HAS_ROS:
        parser.add_argument(
            "--scene-topic",
            type=str,
            default="/socialsituation",
            help="if set, subscribe to this topic for incoming scene 'short codes'.",
        )

    args = parser.parse_args()

    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    bridge = Bridge()

    engine.setInitialProperties({"bridge": bridge})

    def on_incoming_social_situation(msg):

        b64 = msg.data

        frame = minify.decode(b64)
        # print(frame)
        bridge.setScene(frame)

    def on_record_social_situation(msg):

        start, end, seen_by, name = json.loads(msg.data)
        bridge.start_recording(start, end, seen_by, name)

    if HAS_ROS:
        rospy.init_node("social_simulation_simulator", anonymous=True)
        rospy.Subscriber(
            args.scene_topic, String, on_incoming_social_situation, queue_size=1
        )
        rospy.Subscriber(
            "/socialsituation/record", String, on_record_social_situation, queue_size=1
        )

    qml_file = Path(__file__).parent / "app.qml"
    engine.load(qml_file)

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())
