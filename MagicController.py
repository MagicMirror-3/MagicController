import sys
import time
from abc import ABC

# from Configuration import ConfigurationHandler
import cv2

from util import User
from Communication import CommunicationHandler
from FaceRecognition import FaceAuthentication
from FaceRecognition import MirrorFaceOutput
from Configuration import ConfigurationHandler


class Mediator(ABC):
    def notify(self, sender: object, *args) -> None:
        pass


class BaseComponent:

    def __init__(self, mediator: Mediator = None):
        self.mediator = mediator


class MagicController(Mediator):
    def __init__(self, host):
        self.communication_handler = CommunicationHandler(self, host)
        self.face_authentication = FaceAuthentication(benchmark_mode=True,
                                                      lite=True,
                                                      resolution=(640, 480),
                                                      mediator=self,
                                                      threshold=1.0
                                                      )

        # init with the base config, which is user 0
        ConfigurationHandler.updateConfiguration(0)

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
        # communication handler sends request to register a user
        if isinstance(sender, CommunicationHandler.CreateUser):
            callback = args[0]
            user_id = args[1]
            images = args[2]

            # Call FaceAuthentication to register faces
            success = self.face_authentication.register_faces(user_id, images, min_number_faces=4, mode='slow')

            # call callback, to send the response to the http server.
            callback(success)

        # Face Recognition detected a face
        if isinstance(sender, MirrorFaceOutput):
            print("call notify: face detected")
            detected_user_id = args[0]

            if ConfigurationHandler.updateConfiguration(0 if detected_user_id is None else detected_user_id):
                # refresh the mirror layout
                self.communication_handler.refresh_layout()
            else:
                print("Failed to update the configuration.")
        if isinstance(sender, CommunicationHandler.DeleteUser):
            user_id = args[0]

            self.face_authentication.delete_user(user_id)

            print(f"Deleted user: {user_id}")


def main():
    try:
        host = sys.argv[1]
    except IndexError:
        host = None
    MagicController(host)


if __name__ == '__main__':
    main()
