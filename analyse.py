import numpy as np
import json
import sys

from generate_description import describe

INTERPOLATION_FREQUENCY = 2  # Hz
WINDOW_LENGTH = 3  # sec -> number of descriptions/embeddings = INTERPOLATION_FREQUENCY x WINDOW_LENGTH


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
    """resample the situation to freq Hz + shift the timestamp to start at t=0"""

    timestamps = sorted(situation.keys())

    if len(timestamps) < 2:
        print("need at least 2 keyframes to resample")
        return situation

    time_offset = timestamps[0]

    print(
        f"Situation starts at {timestamps[0]}s and ends at {timestamps[-1]}s (duration: {timestamps[-1]-timestamps[0]}s)"
    )

    result = {}

    prev_ts = timestamps[0]
    next_ts = timestamps[1]

    for ts in np.arange(timestamps[0], timestamps[-1] + 0.0001, 1 / freq):

        if ts > next_ts:
            prev_ts = next_ts
            next_ts = [x for x in timestamps if x > ts][0]

        if ts in timestamps:
            result[ts - time_offset] = situation[ts]
        else:
            scene = interpolate(
                situation[prev_ts]["scene"],
                prev_ts,
                situation[next_ts]["scene"],
                next_ts,
                ts,
            )

            result[ts - time_offset] = {
                "scene": scene,
                "ts": ts,
            }

    return result


def get_frames_with_engagement(situation):

    frames = []

    for ts, v in situation.items():
        scene = v["scene"]

        for name, state in scene.items():
            if len(state["engaged_with"]) > 0:
                frames.append((ts, name))

    return frames


def get_frames(situation, range):

    return [situation[ts] for ts in range]


def to_json(situation):

    # workaround to match how javascript's toString: 0.0.toString = "0" and not "0.0"
    def to_str(ts):
        return str(ts if ts != int(ts) else int(ts))

    return json.dumps({to_str(k): v for k, v in situation.items()})


if __name__ == "__main__":

    situation = None

    with open(sys.argv[1], "r") as f:

        # convert keys to floats
        situation = {float(k): v for k, v in json.load(f).items()}

    resampled = resample(situation, freq=INTERPOLATION_FREQUENCY)

    # print(to_json(resampled))

    for ts, name in get_frames_with_engagement(resampled):
        if ts < WINDOW_LENGTH:
            print("Skipping frame as timestamp too early (< WINDOW_LENGTH)")
            continue

        frames = get_frames(
            resampled,
            np.arange(ts - WINDOW_LENGTH, ts + 0.0001, 1 / INTERPOLATION_FREQUENCY),
        )

        print(
            f"\n{name} is engaged at t={ts}s; let's generate the previous {len(frames)} descriptions (from t={ts - WINDOW_LENGTH}s) from {name}'s perspective.\n"
        )

        for f in frames:
            print(f"Scene seen by {name} at t={f['ts']}s")
            desc = describe(f, seen_by=name)
            print(desc)
            print("-------------")
