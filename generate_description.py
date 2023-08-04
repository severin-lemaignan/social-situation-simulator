import random
import math

NAMES = [
    "Oliver",
    "George",
    "William",
    "Jack",
    "James",
    "Thomas",
    "Charlie",
    "Harry",
    "Henry",
    "Alexander",
    "Benjamin",
    "Daniel",
    "Michael",
    "David",
    "Joseph",
    "Matthew",
    "Andrew",
    "Edward",
    "Samuel",
    "Robert",
    "Christopher",
    "Stephen",
    "Richard",
    "Peter",
    "Anthony",
    "Jonathan",
    "Simon",
    "Patrick",
    "Alan",
    "Paul",
    "Nicholas",
    "Timothy",
    "Philip",
    "Francis",
    "Brian",
    "Kevin",
    "Martin",
    "Keith",
    "Graham",
    "Terry",
    "Barry",
    "Derek",
    "Adrian",
    "Wayne",
    "Gary",
    "Stuart",
    "Malcolm",
    "Gavin",
    "Darren",
    "Lee",
    "Olivia",
    "Amelia",
    "Isla",
    "Ava",
    "Emily",
    "Sophia",
    "Lily",
    "Isabella",
    "Mia",
    "Poppy",
    "Ella",
    "Grace",
    "Freya",
    "Scarlett",
    "Chloe",
    "Daisy",
    "Alice",
    "Phoebe",
    "Matilda",
    "Charlotte",
    "Jessica",
    "Lucy",
    "Rosie",
    "Hannah",
    "Ruby",
    "Evelyn",
    "Zoe",
    "Abigail",
    "Erin",
    "Eleanor",
    "Megan",
    "Elizabeth",
    "Victoria",
    "Laura",
    "Rachel",
    "Rebecca",
    "Nicola",
    "Louise",
    "Jennifer",
    "Susan",
    "Karen",
    "Christine",
    "Pamela",
    "Wendy",
    "Angela",
    "Alison",
    "Sharon",
    "Donna",
    "Sandra",
    "Diane",
]

SELF = "robot"
FOV = 100  # field of view, in degrees
FOA = 30  # field of attention (eg 'looking at smthg'), in degrees

FAR = 4  # 'far'distance
CLOSE = 1.5  # 'close distance'
MEDIUM = 3

TRANSFORM_NAMES = True
NAMES_MAP = {}


def r(name):
    if not TRANSFORM_NAMES:
        if name == "robot":
            return "Joe"
        return name

    if name not in NAMES_MAP:
        NAMES_MAP[name] = random.choice(NAMES)

    return NAMES_MAP[name]


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

    if d < CLOSE:
        return CLOSE, "{ag} is close to {ref}"

    if d > FAR:
        return FAR, ""

    if is_facing(ag1, ag2):
        return MEDIUM, "{ag} is not far from {ref}"

    # if the two agents are not really close, or a bit farther away, but facing each other, consider them 'far' from each other
    return FAR, ""


def is_facing(ag1, ag2):
    return is_visible(ag1, ag2) and is_visible(ag2, ag1)


def is_visible(target, base, fov=FOV):

    if target == base:
        return True

    angle = (
        math.atan2(target["y"] - base["y"], target["x"] - base["x"]) * 180 / math.pi
        - base["theta"]
    )

    # wrap angle in -180, 180
    angle = math.remainder(angle * math.pi / 180, 2 * math.pi) * 180 / math.pi

    # print(
    #    f"I'm at {base_x},{base_y},{base_theta}; target at {target_x}, {target_y} -> {angle}"
    # )
    if abs(angle) < fov / 2:
        return True
    else:
        return False


def describe(scene, seen_by=SELF, random_names=True):

    global TRANSFORM_NAMES
    TRANSFORM_NAMES = random_names

    print(f"At {scene['ts']}s:")
    agents = scene["scene"]

    # # only describe if the robot is present in the scene
    if seen_by not in agents:
        print("%s not in the scene. Can not generate description" % seen_by)
        return ""

    ref = agents[seen_by]

    desc = set()

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
            desc.add(motion.format(ag=r(name), ref=r(seen_by)))

        distance, dist_desc = dist(ag, ref)
        if dist_desc:
            desc.add(dist_desc.format(ag=r(name), ref=r(seen_by)))

        if ag["talking"]:
            desc.add(f"{r(name)} is talking")

        for target_name, tg in agents.items():

            if target_name == name:
                continue

            if not is_visible(tg, ref, fov=FOV):
                print(f"{seen_by} can not see {target_name}")
                continue

            if not is_visible(tg, ag, fov=FOV):
                continue

            distance, _ = dist(tg, ag)
            if distance in [CLOSE, MEDIUM]:

                AseesB = is_visible(tg, ag, fov=FOA)
                BseesA = is_visible(ag, tg, fov=FOA)

                if AseesB:
                    if BseesA:
                        names = sorted([name, target_name])
                        desc.add(
                            f"{r(names[0])} and {r(names[1])} are looking at each other"
                        )
                    else:
                        desc.add(f"{r(name)} is looking at {r(target_name)}")
                else:
                    pass
                    # desc.add(f"{r(name)} is not looking at {r(target_name)}")

    return "; ".join(x for x in desc)
