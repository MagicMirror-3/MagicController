import base64
import os
from collections import Counter

import cv2
import numpy as np


class User:
    """
    Represents a user of the mirror.
    """

    def __init__(self, name=None, identifier=None):
        """
        Creates a digital twin of a user of the mirror.

        Args:
            name (str): The name of the user
            identifier (int): A unique identifier of the user. This is needed in case there are multiple users with the
                same name
        """

        self._isDefaultUser = name is None or identifier < 0

        self._name = name
        self._identifier = identifier

    def isRealPerson(self) -> bool:
        """
        Returns whether this user is the default user or a real person.

        Returns:
            bool: true, if this represents a real person
        """

        return not self._isDefaultUser

    def getName(self) -> str:
        """
        Returns the name of this user.

        Returns:
            str: The name of the user
        """

        return self._name

    def getIdentifier(self) -> int:
        """
        Returns the unique identifier of this user.

        Returns:
            int: the identifier of the user
        """

        return self._identifier


class CONSTANTS:
    """
    A class containing useful constant variables.
    """

    # The absolute base path for this folder
    BASE_PATH = os.path.abspath(os.path.dirname(__file__))

    # The path to the directory of the magic mirror
    MAGIC_MIRROR_DIR = os.path.normpath(os.path.join(BASE_PATH, "..", "MagicMirror"))

    # Database file
    DATABASE_PATH = os.path.join(BASE_PATH, "MagicMirrorDB.db")

    # ---------- [ConfigurationHandler] ---------- #
    CONFIG_PATH = os.path.join(MAGIC_MIRROR_DIR, "config")
    CONFIG_FILE = "config.js"
    FULL_CONFIG_PATH = os.path.join(CONFIG_PATH, CONFIG_FILE)

    TEMPLATE_CONFIG = os.path.join(BASE_PATH, "Configuration", "template_config.js")
    TEMPLATE_JSON = os.path.join(BASE_PATH, "Configuration", "template_config.json")


def get_image_from_base64(image_string):
    image_bytes = base64.b64decode(image_string)
    image_numpy_array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(image_numpy_array, flags=1)
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)


def get_ip():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def distance_euclid(vector_1, vector_2):
    """

    :param vector_1: first vector
    :param vector_2: second vector
    :return: euclidean distance
    """

    return np.linalg.norm(vector_1 - vector_2)


def thresholded_knn(dataset, new_point, distance_function, threshold, k):
    """

    :param k:
    :param dataset: tuples with (name, vector)
    :param new_point: new embedding: vector
    :param distance_function: function to calculate distance metric
    :param threshold: above this threshold, a point is classified as "unknown"
    :return: tuple()
    """
    distance_and_label = [(distance_function(point, new_point), label) for label, point in dataset]

    # sort tuples by distance
    distance_and_label.sort(key=lambda x: x[0])

    # get k points with nearest distance
    if len(distance_and_label) >= k:
        k_nearest_neighbours = distance_and_label[:k]
    else:
        k_nearest_neighbours = distance_and_label

    # get most common label, if distance is above threshold, point is classified as unknown
    c = Counter([label if dist < threshold else None for dist, label in k_nearest_neighbours])

    # list of most common labels: (label, count), increasing indices have decreasing count
    most_common_labels = c.most_common(None)

    # when first common label and second common label have same count, return None
    if len(most_common_labels) >= 2 and most_common_labels[0][1] == most_common_labels[1][1]:
        # print(most_common_labels, " : Identified None")
        return None
    # return most common label
    # print(most_common_labels, " : Identified ", most_common_labels[0][0])
    return most_common_labels[0][0]


if __name__ == "__main__":
    v1 = np.array([1, 2, 3]).T
    v2 = np.array([2, 3, 4]).T
    v3 = np.array([3, 1, 2]).T
    v4 = np.array([1, 1, 1]).T
    v5 = np.array([2, 2, 2]).T
    v6 = np.array([1, 3, 3]).T

    dataset = [
        ('p1', v1),
        ('p2', v2),
        ('p1', v3),
        ('p3', v4),
        ('p3', v5),
        ('p2', v6)
    ]

    new_point = np.array([4, 2, 2]).T

    print(thresholded_knn(dataset, new_point, distance_euclid, threshold=2, k=4))
