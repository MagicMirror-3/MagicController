import pickle
import platform
import time

import cv2 as cv
import dlib
from imutils.video import VideoStream
from threading import Timer
import os

import numpy as np

from MobileFaceNetStandard import MobileFaceNetStandard
from MobileFaceNetLite import MobileFaceNetLite


class FaceAuthentication:
    """

    Optimization:

    https://learnopencv.com/speeding-up-dlib-facial-landmark-detector/

    """

    def __init__(self, benchmark_mode=False, lite=False):
        # load face embeddings from file, if file exists and benchmark mode is turned off

        self.benchmark_mode = benchmark_mode

        if not self.benchmark_mode:
            try:
                with open(r"user_embedding.p", "rb") as file:
                    user_backup = pickle.load(file)
                    self.users = user_backup
                    print("Loaded user embeddings!")
            except FileNotFoundError:
                self.users = []
        else:
            self.users = []

        dirname = os.path.dirname(__file__)
        path_shape_predictor = os.path.join(dirname, "model/shape_predictor_5_face_landmarks.dat")

        if lite:
            self.net = MobileFaceNetLite()
            path_mobile_face_net = os.path.join(dirname, "model/MobileFaceNet.tflite")
            self.net.load_model(path_mobile_face_net)
        else:
            self.net = MobileFaceNetStandard()
            path_standard_face_net = os.path.join(dirname, "model/MobileFaceNet.pb")
            self.net.load_model(path_standard_face_net)

        self.active = True
        self.haar_cascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.landmark_detector = dlib.shape_predictor(path_shape_predictor)
        self.detector = dlib.get_frontal_face_detector()

    def detect_biggest_face(self, image):
        """
        Extract the location of the biggest face from an image.
        If there are multiple faces, choose the nearest (biggest) face.

        Format: (x, y, w, h)

        """

        image_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

        # extract faces with haar classifier
        face_locations = self.haar_cascade.detectMultiScale(
            image_gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(50, 50)
        )

        if len(face_locations) > 0:

            # get location of the biggest face
            faces_sizes = [w + h for (x, y, w, h) in face_locations]
            return face_locations[faces_sizes.index(max(faces_sizes))]
        else:
            return None

    def extract_faces_hog(self, image):
        """
        Extract faces from an image using HOG detector
        """

        image_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        return self.detector(image_gray, 1)

    def register_face(self, name, image):
        """

        :param name:
        :param image:
        :return:
        """

        # extract locations of the faces, should be exactly one
        face_locations = self.extract_faces_hog(image)
        if len(face_locations) == 1:
            location = face_locations[0]
            # normalize and extract the face
            face = self.normalize_face(image, location)
        elif len(face_locations) == 0:
            raise Exception("No faces detected!")
        else:
            raise Exception("Multiple faces detected")

        # calculate embedding
        embedding = self.net.calculate_embedding(face)

        # insert into users database
        self.users.append((name, embedding))
        # write face embeddings to pickle file
        if not self.benchmark_mode:
            with open(r"user_embedding.p", "wb") as file:
                pickle.dump(self.users, file)

        print(f"Registered new face for {name}")

    def match_face(self, image, tolerance=0.65):
        """

        :param image:
        :param tolerance:
        :return:
        """

        face_location = self.detect_biggest_face(image)

        if face_location is not None:
            x, y, w, h = face_location
            dlib_rectangle = dlib.rectangle(x, y, x + w, y + h)

            normalized_face = self.normalize_face(image, dlib_rectangle, size=112, padding=0.3)

            # calculate embedding
            unknown_embedding = self.net.calculate_embedding(normalized_face)

            distances = []
            for name, encoding in self.users:
                distances.append(self.distance_euclid(unknown_embedding, encoding))

            if min(distances) <= tolerance:
                return self.users[distances.index(min(distances))][0], min(distances), [(x, y, w, h)]
            else:
                return "unknown", None, None
        else:
            return None, None, None

    @staticmethod
    def distance_euclid(vector_1, vector_2):
        """

        :param vector_1: first vector
        :param vector_2: second vector
        :return: euclidean distance
        """

        return np.linalg.norm(vector_1 - vector_2)

    def normalize_face(self, image, location, size=112, padding=0.3):
        """

        :param padding:
        :param image:
        :param location:
        :param size:
        :return:
        """

        landmarks = self.landmark_detector(image, location)

        # normalize image
        return dlib.get_face_chip(image, landmarks, size=size, padding=padding)

    def stop(self):
        """

        :return:
        """

        self.active = False

    def delete_all_users(self):
        self.users = []

    def live_recognition(self):
        """

        :return:
        """
        print(platform.machine())
        if platform.machine() == "armv7l":
            capture = VideoStream(usePiCamera=True).start()
        else:
            capture = VideoStream(src=0, resolution=(1600,900)).start()

        # main loop
        while self.active:

            frame = capture.read()

            start = time.time()
            match, distance, face_location = self.match_face(frame)
            end = time.time()
            if match is not None and distance is not None:
                print(f"Identified {match}, Dist: {round(distance, 4)}, FPS: {1 / (end - start)}")

            # print(1000 * 10 ** 6 / (end - start), "fps")

            # OpenCV returns bounding box coordinates in (x, y, w, h) order
            # but we need them in (top, right, bottom, left) order, so we
            # need to do a bit of reordering
            if face_location is not None:
                face_location = [(y, x + w, y + h, x) for (x, y, w, h) in face_location]

                # draw rectangles for faces
                for f1, f2, f3, f4 in face_location:
                    frame = cv.rectangle(frame, (f2, f1), (f4, f3), (255, 0, 0), 3)

            # extract faces from image
            # for (y1, x2, y2, x1) in face_locations:
            # face = frame[y1:y2, x1:x2]
            # cv.imshow("face", face)
            # ---------------------------

            cv.imshow('Video', frame)
            if cv.waitKey(20) & 0xFF == ord('d'):
                break

        capture.stop()
        cv.destroyAllWindows()


def localize_faces(image, detector, sample=1):
    """

    :param image:
    :param detector:
    :param sample:
    :return:
    """

    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    return detector(gray, sample)


def main():
    # register faces
    auth = FaceAuthentication(benchmark_mode=True, lite=True)

    dirname = os.path.dirname(__file__)

    path_niklas = os.path.join(dirname, "images/niklas1.jpg")
    path_craig = os.path.join(dirname, "images/craig1.jpg")

    auth.register_face("Niklas", cv.imread(path_niklas))
    auth.register_face("Craig", cv.imread(path_craig))

    auth.live_recognition()


if __name__ == "__main__":
    main()
