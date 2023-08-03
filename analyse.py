import numpy as np
import json
from re import A
import sys


def interpolate(scene_a, t_a, scene_b, t_b, t):

    scene = {}

    for agent in scene_a.keys():
        a = scene_a[agent]
        b = scene_b[agent]

        ab = zip(a.values(), b.values())

        def interp(a, b):

            if type(a) in [int, float]:
                return a + (b - a) / (t_b - t_a) * (t - t_a)
            else:
                return a

        vals = [interp(a, b) for a, b in ab]

        result = a.copy()

        idx = 0
        for k in result:
            result[k] = vals[idx]
            idx += 1

        result["vx"] = a["vx"]
        result["vy"] = a["vy"]

        scene[agent] = result

    return scene


def resample(situation, freq=2):

    timestamps = sorted(situation.keys())

    if len(timestamps) < 2:
        print("need at least 2 keyframes to resample")
        return situation

    # print(
    #    f"Situation starts at {timestamps[0]}s and ends at {timestamps[-1]}s (duration: {timestamps[-1]-timestamps[0]}s)"
    # )

    result = {}

    prev_ts = timestamps[0]
    next_ts = timestamps[1]

    for ts in np.arange(timestamps[0], timestamps[-1] + 0.0001, 1 / freq):

        if ts > next_ts:
            prev_ts = next_ts
            next_ts = [x for x in timestamps if x > ts][0]

        if ts in timestamps:
            # workaround to match how javascript's toString: 0.0.toString = "0" and not "0.0"
            key = str(ts if ts != int(ts) else int(ts))
            result[key] = situation[ts]
        else:
            scene = interpolate(
                situation[prev_ts]["scene"],
                prev_ts,
                situation[next_ts]["scene"],
                next_ts,
                ts,
            )

            # workaround to match how javascript's toString: 0.0.toString = "0" and not "0.0"
            key = str(ts if ts != int(ts) else int(ts))
            result[key] = {
                "scene": scene,
                "ts": ts,
            }

    return result


if __name__ == "__main__":

    situation = None

    with open(sys.argv[1], "r") as f:

        # convert keys to floats
        situation = {float(k): v for k, v in json.load(f).items()}

    resampled = resample(situation)

    print(json.dumps(resampled))
