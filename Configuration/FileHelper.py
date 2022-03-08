from shutil import copyfile

from util import CONSTANTS


def activateConfigFile(filepath: str):
    """
    Activates the given config file by copying it into the main config file.

    Args:
        filepath (str): the path of the new config file

    Returns:
        None: Nothing
    """

    copyfile(filepath, CONSTANTS.CONFIG_FILE)


def updateUserConfiguration(user, configuration):

    # TODO: Save the given configuration into the user file
    pass
