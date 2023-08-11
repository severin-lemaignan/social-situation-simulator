import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize, OptimizeResult

responses = pd.read_csv("votes.csv", index_col=0)
for c in ["vid1", "vid2", "vid3"]:
    responses[c] = responses[c].map(lambda x: x.split("/")[-1][:-4])

videos_to_codes = pd.read_csv("videos_to_codes.csv", index_col=0)
videos_to_codes = {
    k: v["0"] for k, v in videos_to_codes.to_dict(orient="index").items()
}

# A,B,C,1 -> AB < AC
# A,B,C,0 -> A far from both B and C
# A,B,C,-1 -> AB > AC
# responses = [
#    ("A", "B", "C", -1),  # close
#    ("A", "C", "B", 1),  # far
#    ("B", "C", "E", 0), # both far
#    ("A", "B", "D", 0),
#    ("A", "E", "D", 1),
#    ("E", "B", "D", 0),
#    ("D", "C", "A", -1),
#    ("A", "B", "D", 1),
#    ("D", "C", "A", 0),
#    ("D", "C", "A", -1),
#    ("D", "C", "A", 0),
# ]


def generate_social_space(AB_comparisons):

    situations_keys = np.unique(np.array(AB_comparisons)[:, :3].flatten()).tolist()

    distances = {}

    for a, b, c, d in AB_comparisons:

        id1 = "###".join(sorted([a, b]))
        id2 = "###".join(sorted([a, c]))

        if d == 1:
            print(f"{a} closer to {b} than to {c}")

            distances.setdefault(id1, 1)
            distances[id1] *= 0.8
            distances.setdefault(id2, 1)
            distances[id2] *= 1.2

        elif d == -1:
            print(f"{a} closer to {c} than to {b}")

            distances.setdefault(id2, 1)
            distances[id2] *= 0.8
            distances.setdefault(id1, 1)
            distances[id1] *= 1.2

        elif d == 0:
            print(f"{a} far from {b} and {c}")

            distances.setdefault(id2, 1)
            distances[id2] *= 1.2
            distances.setdefault(id1, 1)
            distances[id1] *= 1.2

        elif d == 2:
            print(f"{a} close to both {b} and {c}")

            distances.setdefault(id2, 1)
            distances[id2] *= 0.8
            distances.setdefault(id1, 1)
            distances[id1] *= 0.8

        else:
            assert False

    situations = [
        (k.split("###")[0], k.split("###")[1], v) for k, v in distances.items()
    ]

    # Example pairwise distance inequalities: [(i, j, lower_bound_distance), ...]
    # distance_inequalities = [(0, 1, 3), (1, 2, 2), (0, 2, 4)]
    distance_inequalities = [
        (situations_keys.index(x), situations_keys.index(y), d)
        for x, y, d in situations
    ]

    # Number of vectors
    num_vectors = max(max(pair[:2]) for pair in distance_inequalities) + 1

    dims = 15

    # Initial guess for coordinates
    initial_coordinates = np.random.rand(num_vectors, dims)

    def cb(intermediate_result):
        print(f"Intermediate result: total deviation={objective(intermediate_result)}")

    def objective(coordinates):
        deviations = []

        for i, j, lower_bound_distance in distance_inequalities:
            actual_distance = np.linalg.norm(
                coordinates.reshape(-1, dims)[i] - coordinates.reshape(-1, dims)[j]
            )
            deviation = abs(actual_distance - lower_bound_distance)
            deviations.append(deviation)

            # print(
            #    f"({i}, {j}) - dist: {actual_distance:.3f} - deviation: {deviation:.3f}"
            # )

        dev = sum(deviations)
        # print(dev)
        return dev

    print("\nEstimated distances:")
    for a, b, d in distance_inequalities:
        print(f"- {situations_keys[a]}  <-> {situations_keys[b]}: {d}")

    print("Starting optimization...")
    # Solve the optimization problem
    result = minimize(
        objective,
        initial_coordinates.flatten(),
        method="BFGS",
        options={"maxiter": 20},
        callback=cb,
    )

    return dict(zip(situations_keys, [x for x in result.x.reshape(-1, dims)]))


optimized_coordinates = generate_social_space(
    responses[["vid1", "vid2", "vid3", "choice"]].values
)

print("Optimized coordinates:\n", optimized_coordinates)

df = pd.DataFrame.from_dict(optimized_coordinates, orient="index")
print(df)

ax = df.plot.scatter(x=0, y=1)
for idx, row in df.iterrows():
    ax.annotate(idx, (row[0], row[1]))

plt.show()
