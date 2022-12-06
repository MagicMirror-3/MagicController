import json
import time

from loguru import logger

from DatabaseAdapter import DatabaseAdapter
from util import CONSTANTS

from .FileHelper import FileHelper


class ConfigurationHandler:
    """
    A class handling the switching and saving of config files to enable multiple layouts for the magic mirror.
    """

    @staticmethod
    def updateConfiguration(newUser: int) -> bool:
        """
        Updates the configuration file.

        Args:
            newUser (int): The user id to use the configuration of

        Returns:
            bool: True, if the config file was updates successfully
        """

        logger.debug(f"Loading the configuration from '{newUser}'")

        try:
            # Create the database adapter here to prevent sqlite3 thread error
            database = DatabaseAdapter()

            # Create a string with the contents of the template config
            configFile = FileHelper.readFile(CONSTANTS.TEMPLATE_CONFIG)

            try:
                # Get the layout of the user
                layout = json.loads(database.get_layout_of_user(newUser))

                # Close the connection
                database.close()
            except Exception as e:
                logger.critical(
                    f"Something went wrong while retrieving data from the database: {e}"
                )
                return False

            # Read the JSON template
            templateConfig = FileHelper.readFile(
                CONSTANTS.TEMPLATE_JSON, "json"
            )
            moduleList: list = templateConfig["modules"]

            # Check if modules list ist valid
            if not isinstance(moduleList, list):
                logger.error(f"Modules list is not a list: {moduleList}")
                return False

            # Add the module of the user to the list
            moduleList.extend(layout)

            # Replace the contents in the configFile
            configFile = configFile.replace(
                "'%TEMPLATE_CONFIG%'", json.dumps(templateConfig)
            )

            # Save the contents
            FileHelper.writeFile(CONSTANTS.FULL_CONFIG_PATH, configFile)

            logger.success("Successfully replaced the configuration file")
            return True
        except FileNotFoundError as e:
            logger.critical(f"File not found: '{e.filename}'")
            logger.warning("Is this running in a Magic-Mirror environment?")
            return False


if __name__ == "__main__":
    handler = ConfigurationHandler()
    handler.updateConfiguration(0)

    time.sleep(10)

    handler.updateConfiguration(1)
