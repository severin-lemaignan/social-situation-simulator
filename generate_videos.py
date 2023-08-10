import pandas as pd
import sys
import json
import rospy
from std_msgs.msg import String
import time
from pathlib import Path
from analyse import resample

import minify

if __name__ == "__main__":

    rospy.init_node("generate_video")

    pub = rospy.Publisher("/socialsituation/record", String, queue_size=1)

    def record(start, end, seen_by, filename):
        print("Recording %s..." % filename)
        pub.publish(json.dumps([start, end, seen_by, str(filename)]))

        t = 0
        while t < end - start + 3:
            time.sleep(0.1)
            t += 0.1
            sys.stdout.write(".")
            sys.stdout.flush()

        print("Should be ~done. Hopefully?")

    filename = Path(sys.argv[1])

    with open(filename, "r") as f:

        # convert keys to floats
        situation = {float(k): v for k, v in json.load(f).items()}

    sampling_rate = 2
    window_length = 2

    situation = resample(situation, freq=sampling_rate)

    if Path("videos_to_codes.csv").exists():
        video_codes = {
            k: v["0"]
            for k, v in pd.read_csv("videos_to_codes.csv", index_col=0)
            .to_dict(orient="index")
            .items()
        }
    else:
        video_codes = {}

    for ts, frame in situation.items():

        if ts < window_length:
            continue

        scene = frame["scene"]

        for name, _ in scene.items():
            filename_full = filename.name + "-%s-%s" % (ts, name)
            if filename_full in video_codes:
                print(f"Skipping {filename_full} (already in video_to_codes)")
                continue

            record(
                ts - window_length,
                ts,
                name,
                filename_full,
            )

            code = minify.encode({"scene": frame["scene"], "seen_by": name})
            video_codes[filename_full] = code

    pd.DataFrame.from_dict(video_codes, orient="index").to_csv("videos_to_codes.csv")
