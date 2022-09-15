import sys
from abc import ABC
from loguru import logger

from Communication import CommunicationHandler
from Configuration import ConfigurationHandler
from FaceRecognition import FaceAuthentication
from FaceRecognition import MirrorFaceOutput


# from Configuration import ConfigurationHandler


class Mediator(ABC):
    def notify(self, sender: object, *args) -> None:
        pass


class BaseComponent:

    def __init__(self, mediator: Mediator = None):
        self.mediator = mediator


class MagicController(Mediator):
    def __init__(self, host):
        logger.info("Starting the MagicController...")

        self.communication_handler = CommunicationHandler(self, host)
        self.face_authentication = FaceAuthentication(benchmark_mode=False,
                                                      lite=True,
                                                      resolution=(640, 480),
                                                      mediator=self,
                                                      threshold=1.0
                                                      )

        # Current user is default
        self.current_user_id = 0

        # init with the base config, which is user 0
        ConfigurationHandler.updateConfiguration(self.current_user_id)

        logger.success("MagicController started!")

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

    def _loadUserLayout(self, user_id: int) -> None:
        """
        Updates the layout of the MagicMirror² framework.

        First, the config.js file is updated by the ``ConfigurationHandler`` and on success, the */refresh* route of the
        MagicModule is called. Also, ``self.current_user_id`` is kept up to date.

        Args:
            user_id (int): The ID of the user whose layout should be loaded

        Returns:
            None: Nothing
        """

        logger.debug(f"Swapping layout from {self.current_user_id} to {user_id}")

        # Keep track of the current user and update the layout if the config was updated
        if ConfigurationHandler.updateConfiguration(user_id):
            self.current_user_id = user_id

            self.communication_handler.refresh_layout()

    def notify(self, sender: object, *args) -> None:
        logger.debug(f"Notification from {sender} with the arguments {args}")

        # communication handler sends request to register a user
        if isinstance(sender, CommunicationHandler.CreateUser):
            callback = args[0]
            user_id = args[1]
            images = args[2]

            # Call FaceAuthentication to register faces
            success = self.face_authentication.register_faces(user_id, images, min_number_faces=4, mode='slow')

            logger.debug(f"New user created: {success}")
            # call callback, to send the response to the http server.
            callback(success)

            return

        # Face Recognition detected a face
        if isinstance(sender, MirrorFaceOutput):
            detected_user_id: int = 0 if args[0] is None else int(args[0])
            logger.debug(f"User {detected_user_id} detected!")

            self._loadUserLayout(detected_user_id)

            return

        # A user is deleted
        if isinstance(sender, CommunicationHandler.DeleteUser):
            user_id = args[0]

            self.face_authentication.delete_user(user_id)

            # Restore the default layout if the user was logged on
            if user_id == self.current_user_id:
                self._loadUserLayout(0)

            logger.debug(f"Deleted user: {user_id}")

            return

        # Layout is updated of a user
        if isinstance(sender, CommunicationHandler.SetLayout):
            user_id: int = 0 if args[0] is None else int(args[0])

            # Update the MM2 config file if the user is currently detected
            if user_id == self.current_user_id:
                self._loadUserLayout(user_id)

            return

        logger.warning("This notification was not handled correctly!")


@logger.catch
def main():
    try:
        host = sys.argv[1]
    except IndexError:
        host = None

    # Init the logger with a new file every day
    logger.add("logs/{time:YYYY:MM:DD}.log", rotation="12:00", enqueue=True, backtrace=True, diagnose=True)

    MagicController(host)


if __name__ == '__main__':
    main()
