import json
import zlib
import base64


def encode(frame):
    try:
        scene = frame["scene"]
        del frame["scene"]

        fields = list(list(scene.items())[0][1].keys())
        vals = []
        for name, state in scene.items():
            vals.append(name)
            vals += list(state.values())

        desc = json.dumps((fields, vals, frame))

        cmpstr = zlib.compress(desc.encode("utf-8"))

        return base64.b64encode(cmpstr)
    except Exception:
        return ""


def decode(base64_desc):

    try:
        cmpstr = base64.b64decode(base64_desc)
        uncmpstr = zlib.decompress(cmpstr)
        fields, vals, rest = json.loads(uncmpstr)

        nb_fields = len(fields)

        entries = [
            vals[x : x + nb_fields + 1] for x in range(0, len(vals), nb_fields + 1)
        ]

        scene = {}
        for e in entries:
            name = e[0]
            scene[name] = dict(zip(fields, e[1:]))

        frame = {"scene": scene}
        frame.update(rest)
        return frame
    except Exception as e:
        print(e)
        return {}


if __name__ == "__main__":

    json_test = """
    {"scene":{
        "robot": {
            "x": 0.040000000000000036,
            "y": 0.16000000000000014,
            "theta": -103.9283419391537,
            "vx": -0.016666666666666607,
            "vy": -0.023333333333333428,
            "talking": false,
            "engaged_with": []
        },
        "Emily": {
            "x": -2.65,
            "y": -2.58,
            "theta": 36.25383773744479,
            "vx": 0.09000000000000004,
            "vy": 0.06999999999999992,
            "talking": false,
            "engaged_with": []
        },
        "Will": {
            "x": -0.9199999999999999,
            "y": -3.62,
            "theta": 37.234833981574674,
            "vx": 0.31400000000000006,
            "vy": 0.5800000000000001,
            "talking": false,
            "engaged_with": []
        },
        "Violet": {
            "x": -3.3499999999999996,
            "y": 1.7800000000000002,
            "theta": 0,
            "vx": 1.1766666666666665,
            "vy": 0.0033333333333332325,
            "talking": false,
            "engaged_with": []
        },
        "Jane": {
            "x": 3.49,
            "y": -2.54,
            "theta": -172.9542308751325,
            "vx": -1.018666666666667,
            "vy": 0.06400000000000006,
            "talking": false,
            "engaged_with": []
        }
    },
    "seen_by": "Jane"
    }

    """
    json_test2 = """
    {"scene":{
        "robot": {
            "x": 0.040000000000000036,
            "y": 0.16000000000000014,
            "theta": -103.9283419391537,
            "vx": -0.016666666666666607,
            "vy": -0.023333333333333428,
            "talking": false,
            "engaged_with": []
        }
        }
    }
    """

    o = json.loads(json_test, parse_float=lambda x: round(float(x), 2))
    o2 = json.loads(json_test2, parse_float=lambda x: round(float(x), 2))

    encoded = encode("fdsfsg fsd ")
    print(decode(" dfdgfdg "))

    print(o)
    encoded = encode(o)
    print("(len: %s)  %s" % (len(encoded), encoded))
    print(decode(encoded))

    encoded = encode(o2)
    print("(len: %s)  %s" % (len(encoded), encoded))
    print(decode(encoded))
