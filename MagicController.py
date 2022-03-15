import time
from abc import ABC

# from Configuration import ConfigurationHandler
from util import User
from Communication import CommunicationHandler
from FaceRecognition import FaceAuthentication


class Mediator(ABC):
    def notify(self, sender: object, *args) -> None:
        pass


class BaseComponent:

    def __init__(self, mediator: Mediator = None):
        self.mediator = mediator


class MagicController(Mediator):
    def __init__(self):
        self.communication_handler = CommunicationHandler(self)
        self.face_authentication = FaceAuthentication(self)

    '''
        self._currentUser = User()
        self._configurationHandler = ConfigurationHandler()
        self.userDetected(self._currentUser)

    def getCurrentUser(self) -> User:
        """
        Gets user which is currently logged on. This might also be the default user.

        Returns:
            User: The user which is logged onto the mirror.
        """

        return self._currentUser

    def userDetected(self, detectedUser: User):
        """
        This method is called by the face recognition if a user is detected. It prompts the ConfigurationHandler to
        update the config file

        Args:
            detectedUser (User): The user which was detected by the camera

        Returns:

        """

        if detectedUser.getIdentifier() != self._currentUser.getIdentifier():
            self._configurationHandler.updateConfiguration(detectedUser)

            self._currentUser = detectedUser

            # TODO: Notify the CommunicationHandler to tell the module to refresh

    '''

    def notify(self, sender: object, *args) -> None:
        if type(sender) == CommunicationHandler.CreateUser:
            callback = args[0]
            user_id = args[1]
            images = args[2]

            # Call FaceAuthentication
            success = self.face_authentication.register_faces(user_id, images, min_number_faces=1, mode='fast')

            # call callback, to send the response to the http server.
            callback(success)
        if type(sender) == FaceAuthentication:
            pass

    def trigger_refresh(self):
        print("Mirror Refresh")


def main():
    MagicController()


if __name__ == '__main__':
    main()
