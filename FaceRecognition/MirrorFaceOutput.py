from threading import Timer


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
            print('#' * 50)
            print(f"Change Layout to: {detected_user}")
            if self.mediator is not None:
                self.mediator.notify(self, detected_user)
            print('#' * 50)

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

        # Timer has passed
        print('#' * 50)
        print(f"Face from {user} no longer detected: Change Layout back to standard")
        if self.mediator is not None:
            self.mediator.notify(self, None)
        print('#' * 50)

        self.current_identified_user = None
