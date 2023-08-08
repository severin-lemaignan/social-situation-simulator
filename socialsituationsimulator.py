#! python3

import sys

import os
import argparse

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

# required to encode/decode scenes' 'short code'
import zlib
import base64

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

    if HAS_ROS:
        rospy.init_node("social_simulation_simulator", anonymous=True)
        rospy.Subscriber(
            args.scene_topic, String, on_incoming_social_situation, queue_size=1
        )

    qml_file = Path(__file__).parent / "app.qml"
    engine.load(qml_file)

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())
