import math

SELF = "robot"
FOV = 100  # field of view, in degrees
FOA = 30  # field of attention (eg 'looking at smthg'), in degrees

FAR = 4  # 'far'distance
CLOSE = 1.5  # 'close distance'


def relative_motion(ag, base):
    vx = ag["vx"]
    vy = ag["vy"]
    norm_v = math.sqrt(vx ** 2 + vy ** 2)

    # agent is ~static?
    if norm_v < 0.2:
        return ""

    dx = ag["x"] - base["x"]
    dy = ag["y"] - base["y"]
    norm_d = math.sqrt(dx ** 2 + dy ** 2)

    # agent is too far or too close to describe relative motion
    if norm_d > FAR or norm_d < CLOSE:
        return ""

    dot = vx * dx + vy * dy

    cos = dot / (norm_d * norm_v)

    if cos < -0.7:
        return "{ag} is walking towards {ref}"
    if cos > 0.7:
        return "{ag} is walking away from {ref}"
    if abs(cos) < 0.3:
        return "{ag} is passing by"

    return ""


def dist(ag1, ag2):

    d = math.sqrt(
        (ag2["x"] - ag1["x"]) * (ag2["x"] - ag1["x"])
        + (ag2["y"] - ag1["y"]) * (ag2["y"] - ag1["y"])
    )
    # print(f"distance: {d}")

    if d < CLOSE:
        return "close to"

    if d > FAR:
        return "far from"

    return ""


def is_visible(target, base, fov=FOV):

    angle = (
        math.atan2(target["y"] - base["y"], target["x"] - base["x"]) * 180 / math.pi
        - base["theta"]
    )

    # print(
    #    f"I'm at {base_x},{base_y},{base_theta}; target at {target_x}, {target_y} -> {angle}"
    # )
    if abs(angle) < fov / 2:
        return True
    else:
        return False


def describe(scene, seen_by=SELF):

    agents = scene["scene"]

    # # only describe if the robot is present in the scene
    if seen_by not in agents:
        print("%s not in the scene. Can not generate description" % seen_by)
        return ""

    ref = agents[seen_by]

    desc = ""

    for name, ag in agents.items():

        if name == seen_by:
            continue

        if not is_visible(ag, ref):
            # print(f"{name} not visible")
            continue
        # print(f"{name} visible")

        # desc += f"{seen_by} sees {name}; "
        motion = relative_motion(ag, ref)
        if motion:
            desc += motion.format(ag=name, ref=seen_by) + "; "

        distance = dist(ag, ref)
        if distance:
            desc += f"{name} is {distance} {seen_by}; "

        if ag["talking"]:
            desc += f"{name} is talking; "

        for target_name, tg in agents.items():

            if target_name == name:
                continue

            distance = dist(tg, ag)
            # add 'looking at' only if A is not far from B
            if "far" not in distance:

                AseesB = is_visible(tg, ag, fov=FOA)
                BseesA = is_visible(ag, tg, fov=FOA)

                if AseesB and BseesA:
                    desc += f"{name} and {target_name} are looking at each other; "
                elif AseesB:
                    desc += f"{name} is looking at {target_name}; "

    return desc
