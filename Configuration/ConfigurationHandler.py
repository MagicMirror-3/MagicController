import json
import time

from Configuration import FileHelper
from DatabaseAdapter import DatabaseAdapter
from util import User, CONSTANTS


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
                print(f"Something went wrong while retrieving data from the database: {e}")
                return False

            # Read the JSON template
            templateConfig = FileHelper.readFile(CONSTANTS.TEMPLATE_JSON, "json")
            moduleList: list = templateConfig["modules"]

            # Check if modules list ist valid
            if not isinstance(moduleList, list):
                print(f"Modules list is not a list: {moduleList}")
                return False

            # Add the module of the user to the list
            moduleList.extend(layout)

            # Replace the contents in the configFile
            configFile = configFile.replace("'%TEMPLATE_CONFIG%'", json.dumps(templateConfig))

            # Save the contents
            FileHelper.writeFile(CONSTANTS.FULL_CONFIG_PATH, configFile)

            return True
        except FileNotFoundError as e:
            print(f"File not found: {e}")
            return False


if __name__ == '__main__':
    handler = ConfigurationHandler()
    handler.updateConfiguration(0)

    time.sleep(10)

    handler.updateConfiguration(1)
