import cv2 as cv
import face_recognition as fr
import imutils
from threading import Timer

import numpy as np


def distance_euclid(enc1, enc2):
    return np.linalg.norm(enc1 - enc2)


class FaceAuth:
    """

    """

    def __init__(self):
        self.users = []
        self.active = True
        self.capture = cv.VideoCapture(0)
        self.buffer_size = 50
        self.haar_cascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.last_number_faces = 0
        self.detect_anyways = False  # identify faces again in x seconds when only unknown faces have been found
        self.timer = None

    def register_face(self, name, image):
        """

        :param name:
        :param image:
        :return:
        """

        # use first face it can find
        self.users.append((name, fr.face_encodings(image)[0]))

    def match_face(self, image, location, tolerance=0.55):
        """

        :param image:
        :param location:
        :param tolerance:
        :return:
        """

        unknown_encoding = fr.face_encodings(image, known_face_locations=[location])[0]

        distances = []
        for name, encoding in self.users:
            distances.append(distance_euclid(unknown_encoding, encoding))

        if min(distances) <= tolerance:
            return self.users[distances.index(min(distances))][0], min(distances)
        else:
            return "unknown", -1

    def stop(self):
        """

        :return:
        """

        self.active = False

    def start(self):
        """

        :return:
        """

        face_count_buffer = [0] * self.buffer_size
        output = MirrorFaceOutput()

        # main loop
        while self.active:
            _, frame = self.capture.read()

            # scale image down
            # frame = imutils.resize(frame, width=500)

            frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            # ---------------------------

            # detect faces in image with haar classifier
            face_locations = self.haar_cascade.detectMultiScale(
                frame_gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(60, 60)
            )
            # OpenCV returns bounding box coordinates in (x, y, w, h) order
            # but we need them in (top, right, bottom, left) order, so we
            # need to do a bit of reordering
            face_locations = [(y, x + w, y + h, x) for (x, y, w, h) in face_locations]

            # buffer number of faces
            face_count_buffer.append(len(face_locations))
            face_count_buffer.pop(0)
            # number of faces is maximum occurring number in last x frames
            number_of_faces = max(face_count_buffer, key=face_count_buffer.count)

            # only check identity if number of faces has changed in last X frames or the detect_anyways flag is set
            # Checking identity is computationally expensive
            if number_of_faces != self.last_number_faces or self.detect_anyways:
                self.detect_anyways = False
                if number_of_faces != 0:
                    # when there are multiple faces, only identify the first one
                    # if this is unknown, identify the second one.
                    for face_location in face_locations:
                        # identify face
                        name = self.match_face(frame_rgb, location=face_location)
                        if name != ('unknown', -1):
                            # output to mirror
                            output.face_detected(name[0])

                            self.last_number_faces = number_of_faces
                            break

                    self.last_number_faces = number_of_faces

                    # no faces identified, after x seconds, identify again, even if number of faces doesn´t change
                    if self.timer is not None and not self.timer.is_alive():
                        self.timer = Timer(2, self.detected_unknown_face)
                        self.timer.start()
                else:
                    # no faces have been detected
                    self.last_number_faces = number_of_faces
                    output.no_faces()

            # draw rectangles for faces
            for f1, f2, f3, f4 in face_locations:
                frame = cv.rectangle(frame, (f2, f1), (f4, f3), (255, 0, 0), 3)

            # extract faces from image
            # for (y1, x2, y2, x1) in face_locations:
            # face = frame[y1:y2, x1:x2]
            # cv.imshow("face", face)
            # ---------------------------

            cv.imshow('Video', frame)
            if cv.waitKey(20) & 0xFF == ord('d'):
                break

        self.capture.release()
        cv.destroyAllWindows()

    def detected_unknown_face(self):
        """

        :return:
        """

        self.detect_anyways = False


class MirrorFaceOutput:
    """

    """

    def __init__(self):
        self.recognized_faces = dict()
        self.timeout = 5
        self.current_identified_user = None
        self.timer = None

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
            print(f"Identified: {detected_user}")

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
        print(f"Face from {user} no longer detected")
        self.current_identified_user = None


def main():
    # register faces
    auth = FaceAuth()
    auth.register_face("Niklas", cv.imread("images/test/Niklas.jpg"))
    auth.register_face("Craig", cv.imread("images/known/craig1.jpg"))

    auth.start()


if __name__ == "__main__":
    main()
