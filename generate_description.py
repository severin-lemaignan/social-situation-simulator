import math

SELF = "robot"
FOV = 100  # field of view, in degrees
FOA = 30  # field of attention (eg 'looking at smthg'), in degrees


def dist(ag1, ag2):

    d = math.sqrt(
        (ag2["x"] - ag1["x"]) * (ag2["x"] - ag1["x"])
        + (ag2["y"] - ag1["y"]) * (ag2["y"] - ag1["y"])
    )
    # print(f"distance: {d}")

    if d < 1:
        return "close to"

    if d > 4:
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

        desc += f"{seen_by} sees {name}; "

        distance = dist(ag, ref)
        if distance:
            desc += f"{name} is {distance} {seen_by}; "

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
