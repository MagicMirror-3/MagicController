from Configuration import ConfigurationHandler
from util import User


class MagicController:
    def __init__(self):
        self._currentUser: User = User()
        self._configurationHandler = ConfigurationHandler()

        # Use the default user config
        self.userDetected(self._currentUser)

    def getCurrentUser(self) -> User:
        """
        Gets user which is currently logged on. This might also be the default user.

        Returns:
            User: The user which is logged onto the mirror.
        """

        return self._currentUser

    def userDetected(self, detectedUser):
        """
        This method is called by the face recognition if a user is detected. It prompts the ConfigurationHandler to
        update the config file

        Args:
            detectedUser (User): The user which was detected by the camera

        Returns:

        """

        if detectedUser.getIdentifier() != self._currentUser.getIdentifier() or not self._currentUser.isRealPerson():
            self._configurationHandler.updateConfiguration(detectedUser)

            # TODO: Notify the CommunicationHandler to tell the module to refresh


def main():
    MagicController()


if __name__ == '__main__':
    main()
