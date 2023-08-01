import math

SELF = "robot"
FOV = 120  # field of view, in degrees
FOA = 60  # field of attention (eg 'looking at smthg'), in degrees


def dist(x1, y1, x2, y2):

    d = math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))

    if d < 1:
        return "close to"

    if d > 2:
        return "far from"

    return ""


def is_visible(target_x, target_y, base_x, base_y, base_theta, fov=FOV):

    angle = (
        math.atan2(target_y - base_y, target_x - base_x) * 180 / math.pi - base_theta
    )

    if abs(angle) < fov / 2:
        return True
    else:
        return False


def describe(agents):

    # only describe if the robot is present in the scene
    if SELF not in agents:
        return ""

    rx, ry, rtheta = agents[SELF]

    desc = ""

    for name, (x, y, theta) in agents.items():

        if name == SELF:
            continue

        if not is_visible(x, y, rx, ry, rtheta):
            continue

        desc += f"I see {name}; "

        distance = dist(x, y, rx, ry)
        if distance:
            desc += f"{name} is {distance} me; "

        for target_name, (target_x, target_y, _) in agents.items():

            if target_name == name:
                continue

            if is_visible(target_x, target_y, x, y, theta, fov=FOA):
                desc += f"{name} is looking at {target_name}; "

    return desc
