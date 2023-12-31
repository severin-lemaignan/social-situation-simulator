#! python3

import numpy as np
import json
import csv
import argparse
from canonical_descriptions import canonize

import generate_description
from generate_description import describe
import minify

DEFAULT_INTERPOLATION_FREQUENCY = 2  # Hz
DEFAULT_WINDOW_LENGTH = 3  # sec -> number of descriptions/embeddings = INTERPOLATION_FREQUENCY x WINDOW_LENGTH


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


def to_csv(
    csv_file,
    situation,
    window_length,
    sampling_rate,
    egocentric=True,
    normalised_names=True,
):

    rows = []

    for ts, v in situation.items():

        if ts < window_length:
            continue

        scene = v["scene"]

        for name, state in scene.items():
            engaged = 0
            if len(state["engaged_with"]) > 0:
                engaged = 1

            frames = get_frames(
                situation,
                np.arange(ts - window_length, ts + 0.0001, 1 / sampling_rate),
            )

            descriptions = [
                (
                    describe(
                        f,
                        seen_by=name,
                        egocentric=egocentric,
                        normalise_names=normalised_names,
                    ),
                    minify.encode({"scene": f["scene"], "seen_by": name}),
                )
                for f in reversed(frames)
            ]

            canonical_descriptions, mapping = canonize(
                [d for d, _ in descriptions], maintain_mapping=False
            )

            full_descs = [
                item
                for pair in zip(
                    canonical_descriptions, [code for _, code in descriptions]
                )
                for item in pair
            ]

            seen_by = generate_description.r(name)
            if seen_by[1:-1] in mapping:
                seen_by = "{%s}" % seen_by[1:-1]
            else:
                # name not present in the mapping because 'self' was not part
                # of any description. In that case, simply add 'as it', since
                # it was not transformed.
                pass

            rows.append([engaged, seen_by, ts] + full_descs)

    header = ["engaged", "viewed_by", "actual_ts"]
    for ts in list(np.arange(0, window_length + 0.001, 1 / sampling_rate)):
        header += ["t-%s" % ts, "t-%s-short-code" % ts]

    csv_writer = csv.writer(csv_file, quoting=csv.QUOTE_NONNUMERIC)
    csv_writer.writerow(header)
    for row in rows:
        csv_writer.writerow(row)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Pre-process and generate descriptions for social situations generated by SocialSituationSimulator"
    )
    parser.add_argument(
        "-s",
        "--sampling-rate",
        type=float,
        nargs="?",
        default=DEFAULT_INTERPOLATION_FREQUENCY,
        help="(Hz) resampling rate of the situation. Default to %sHz."
        % DEFAULT_INTERPOLATION_FREQUENCY,
    )
    parser.add_argument(
        "-l",
        "--window-length",
        type=float,
        nargs="?",
        default=DEFAULT_WINDOW_LENGTH,
        help="(secs) length of the window for which descriptions are generated before each point. Default to %ss."
        % DEFAULT_WINDOW_LENGTH,
    )
    parser.add_argument(
        "-r",
        "--original-names",
        action="store_true",
        help="if set, use simulator names for the agents. If not, names are normalised to abstract values.",
    )
    parser.add_argument(
        "--egocentric",
        action="store_true",
        help="if set, the descriptions are egocentric (eg, uses 'I', 'me' to talk about the agent describing the scene).",
    )
    parser.add_argument(
        "-j",
        "--json",
        type=str,
        nargs="?",
        help="if filename provided, export resampled data to JSON to that file. The file can then be reimported in the simulator.",
    )

    parser.add_argument(
        "-c",
        "--csv",
        type=str,
        nargs="?",
        help="if filename provided, export to CSV to that file",
    )

    parser.add_argument(
        "src",
        type=str,
        help="JSON file containing the situation",
    )

    args = parser.parse_args()

    situation = None

    with open(args.src, "r") as f:

        # convert keys to floats
        situation = {float(k): v for k, v in json.load(f).items()}

    resampled = resample(situation, freq=args.sampling_rate)

    # print(to_json(resampled))

    if args.csv:
        with open(args.csv, "w") as f:
            to_csv(
                f,
                resampled,
                args.window_length,
                args.sampling_rate,
                egocentric=args.egocentric,
                normalised_names=not args.original_names,
            )

    elif args.json:
        with open(args.json, "w") as f:
            f.write(to_json(resampled))

    else:

        for ts, name in get_frames_with_engagement(resampled):
            if ts < args.window_length:
                print("Skipping frame as timestamp too early (< WINDOW_LENGTH)")
                continue

            frames = get_frames(
                resampled,
                np.arange(ts - args.window_length, ts + 0.0001, 1 / args.sampling_rate),
            )

            print(
                f"\n{name} is engaged at t={ts}s; let's generate the previous {len(frames)} descriptions (from t={ts - args.window_length}s) from {name}'s perspective.\n"
            )

            for f in frames:
                print(f"Scene seen by {name} at t={f['ts']}s")
                desc = describe(f, seen_by=name)
                print(desc)
                print("-------------")
