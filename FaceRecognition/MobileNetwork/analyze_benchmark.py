import pandas as pd
import matplotlib.pyplot as plt

"""

"""

df = pd.read_csv("results.csv")

t1 = df[df["n_training_images"] == 0]
t2 = df[df["n_training_images"] == 1]
t3 = df[df["n_training_images"] == 2]
t4 = df[df["n_training_images"] == 3]
t5 = df[df["n_training_images"] == 4]

dfs = [t1, t2, t3, t4, t5]


# calculate the FAR and the FRR
def FAR(df):
    return df[df["true_name"] != df["predicted_name"]].shape[0] / df.shape[0]


def FRR(df, tolerance):
    """
    The two names are the same, but the distance is above the threshold

    :param df:
    :param tolerance:
    :return:
    """

    correctly_classified = df[df["true_name"] == df["predicted_name"]]
    number_of_false_rejects = correctly_classified[correctly_classified["smallest_distance"] > tolerance].shape[0]

    return number_of_false_rejects / df.shape[0]


print("FAR")
for frame in dfs:
    print(FAR(frame))

print("\nFRR 0.5")
for frame in dfs:
    print(FRR(frame, 0.5))

print("\nFRR 0.6")
for frame in dfs:
    print(FRR(frame, 0.6))

print("\nFRR 0.65")
for frame in dfs:
    print(FRR(frame, 0.65))

print("\nFRR 0.7")
for frame in dfs:
    print(FRR(frame, 0.7))

print("\nFRR 0.8")
for frame in dfs:
    print(FRR(frame, 0.8))
