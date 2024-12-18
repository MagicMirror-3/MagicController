from threading import Timer
from loguru import logger


class MirrorFaceOutput:
    """

    """

    def __init__(self, mediator):
        self.timeout = 10
        self.current_identified_user = None
        self.timer = None
        self.mediator = mediator

    def face_detected(self, detected_user):
        """

        :param detected_user:
        :return:
        """

        # if the current user is not None, the timers have to be stopped
        if self.current_identified_user is not None:
            # new face detected, stop timer
            self.timer.cancel()

        if detected_user != self.current_identified_user:
            if self.mediator is not None:
                self.mediator.notify(self, detected_user)

            # set new detected user
            self.current_identified_user = detected_user

        # create a new timer
        self.timer = Timer(self.timeout, self.face_timeout, args=[detected_user])

    def no_faces(self):
        """

        :return:
        """

        # start timer, when no face is detected
        try:
            self.timer.start()
        except:
            pass

    def face_timeout(self, user):
        """

        :param user:
        :return:
        """

        logger.debug(f"No face detected for {self.timeout}s. Swapping back to default!")

        # Timer has passed
        if self.mediator is not None:
            self.mediator.notify(self, None)

        self.current_identified_user = None
