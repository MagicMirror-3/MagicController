import matplotlib.pyplot as plt
import numpy
import numpy as np
import pandas as pd

"""

"""

df = pd.read_csv("results.csv")

t1 = df[df["n_training_images"] == 0]
t2 = df[df["n_training_images"] == 1]
t3 = df[df["n_training_images"] == 2]
t4 = df[df["n_training_images"] == 3]
t5 = df[df["n_training_images"] == 4]

dfs = [t1, t2, t3, t4, t5]


def CCR(threshold, df):
    """
    Correct Classification Rate:

    Number of correct classified persons (distance < threshold) / total number of classifications
    """

    correctly_classified = df[df["true_name"] == df["predicted_name"]]

    return (
        correctly_classified[
            correctly_classified["smallest_distance"] < threshold
        ].shape[0]
        / df.shape[0]
    )


# calculate the FAR and the FRR
def FAR(threshold, df):
    """
    False Acceptance Rate:

    Number of times, someone is wrongly identified as someone else/ total number of identifications

    Someone is identified as someone else, when he is below the acceptance threshold
    """
    wrong_classified = df[df["true_name"] != df["predicted_name"]]
    false_accepts = wrong_classified[
        wrong_classified["smallest_distance"] < threshold
    ]

    return false_accepts.shape[0] / df.shape[0]


def FRR(threshold, df):
    """
    False Rejection Rate:

    Number of correctly classified people, whose shortest distance is above the threshold

    :param df:
    :param threshold:
    :return:
    """

    correctly_classified = df[df["true_name"] == df["predicted_name"]]
    false_rejects = correctly_classified[
        correctly_classified["smallest_distance"] > threshold
    ]

    return false_rejects.shape[0] / df.shape[0]


def createGraph(evaluation_function, df_list, title, ylabel):
    colors = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple"]

    threshold_steps = np.linspace(0, 1, num=100)

    plt.figure()
    ax = plt.subplot(111)
    ax.set_xlabel("Threshold")
    ax.set_ylabel(ylabel)

    for i, frame in enumerate(df_list):
        measure = []
        for threshold in threshold_steps:
            measure.append(evaluation_function(threshold, frame))
        ax.plot(
            threshold_steps,
            measure,
            color=colors[i],
            label=f"{i + 1} training images",
        )

    plt.title(title)
    plt.legend()
    plt.show()


createGraph(
    CCR,
    dfs,
    "Correct Classification Rate depending on threshold",
    "Correct Classification Rate",
)
createGraph(
    FAR,
    dfs,
    "False Acceptance Rate depending on threshold",
    "False Acceptance Rate",
)
createGraph(
    FRR,
    dfs,
    "False Rejection Rate depending on threshold",
    "False Rejection Rate",
)
