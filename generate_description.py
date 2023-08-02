import math

SELF = "robot"
FOV = 100  # field of view, in degrees
FOA = 30  # field of attention (eg 'looking at smthg'), in degrees


def dist(x1, y1, x2, y2):

    d = math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))
    # print(f"distance: {d}")

    if d < 1:
        return "close to"

    if d > 4:
        return "far from"

    return ""


def is_visible(target_x, target_y, base_x, base_y, base_theta, fov=FOV):

    angle = (
        math.atan2(target_y - base_y, target_x - base_x) * 180 / math.pi - base_theta
    )

    # print(
    #    f"I'm at {base_x},{base_y},{base_theta}; target at {target_x}, {target_y} -> {angle}"
    # )
    if abs(angle) < fov / 2:
        return True
    else:
        return False


def describe(scene):

    agents = scene["agents"]

    # only describe if the robot is present in the scene
    if SELF not in agents:
        return ""

    rx, ry, rtheta = agents[SELF]

    desc = ""

    for name, (x, y, theta) in agents.items():

        if name == SELF:
            continue

        if not is_visible(x, y, rx, ry, rtheta):
            # print(f"{name} not visible")
            continue
        # print(f"{name} visible")

        desc += f"I see {name}; "

        distance = dist(x, y, rx, ry)
        if distance:
            desc += f"{name} is {distance} me; "

        for target_name, (target_x, target_y, target_theta) in agents.items():

            if target_name == name:
                continue

            distance = dist(target_x, target_y, x, y)
            # add 'looking at' only if A is not far from B
            if "far" not in distance:

                AseesB = is_visible(target_x, target_y, x, y, theta, fov=FOA)
                BseesA = is_visible(x, y, target_x, target_y, target_theta, fov=FOA)

                if AseesB and BseesA:
                    desc += f"{name} and {target_name} are looking at each other; "
                elif AseesB:
                    desc += f"{name} is looking at {target_name}; "

    return desc
