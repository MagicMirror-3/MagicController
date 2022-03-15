import json
from typing import Union


class FileHelper:
    @staticmethod
    def readFile(filepath: str, mode="str") -> Union[str, dict, list]:
        """
        Reads the contents of the file at the given path.

        Args:
            filepath (str): The path to the file
            mode (str): Either "str" to return the file contents as a string, or "json" to directly parse the contents if
                they're in JSON format

        Returns:
            Union[str, dict, list]: A str is returned if the mode is set to str, otherwise it returns either a map or a list
        """

        with open(filepath) as file:
            if mode == "str":
                return file.read()
            elif mode == "json":
                return json.load(file)

    @staticmethod
    def writeFile(filepath: str, contents: str, mode="w"):
        """
        Writes the given contents to the file at the given location

        Args:
            filepath (str): The path to the file
            contents (str): The contents to write to the file
            mode (str): The mode the file should be opened with.
                See https://docs.python.org/3.10/library/functions.html#open for more information

        Returns:
            None: Nothing
        """

        with open(filepath, mode) as file:
            file.write(contents)
