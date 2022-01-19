import os

import FileHelper
from util import User, CONSTANTS


class ConfigurationHandler:
    """
    A class handling the switching and saving of config files to enable multiple layouts for the magic mirror.
    """

    @staticmethod
    def updateConfiguration(newUser) -> None:
        """
        Updates the configuration file.

        Args:
            newUser (User): The user to use the configuration of

        Returns:
            None: Nothing
        """

        configFile = CONSTANTS.DEFAULT_CONFIG
        if newUser.isRealPerson():
            configFile = newUser.getIdentifier()

        FileHelper.activateConfigFile(os.path.join(CONSTANTS.CONFIG_PATH, configFile))

    @staticmethod
    def saveConfiguration(user, configuration) -> None:
        """
        Save the given configuration for the given user.

        Args:
            user (User): The user to save the configuration of
            configuration (): The new configuration

        Returns:
            None: Nothing
        """

        # TODO: Convert config to string
        FileHelper.updateUserConfiguration(user, configuration)
