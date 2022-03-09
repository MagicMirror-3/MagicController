import base64
import os

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
            identifier (str): A unique identifier of the user. This is needed in case there are multiple users with the
                same name
        """

        self._isDefaultUser = name is None

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

    def getIdentifier(self) -> str:
        """
        Returns the unique identifier of this user.

        Returns:
            str: the identifier of the user
        """

        return self._identifier


class CONSTANTS:
    """
    A class containing useful constant variables.
    """

    MAGIC_MIRROR_DIR = "."  # TODO: determine reliably

    # ---------- [ConfigurationHandler] ---------- #
    CONFIG_PATH = os.path.join(MAGIC_MIRROR_DIR, "config")
    CONFIG_FILE = "config.js"
    DEFAULT_CONFIG = "default_config.js"


def get_image_from_base64(image_string):
    image_bytes = base64.b64decode(image_string)
    image_numpy_array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(image_numpy_array, flags=1)
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
