import pickle
import time

import cv2 as cv
import dlib
from imutils.video import VideoStream
from threading import Timer

import numpy as np

from MobileFaceNet import MobileFaceNet


def distance_euclid(enc1, enc2):
    return np.linalg.norm(enc1 - enc2)


def localize_faces(image, detector, sample=1):
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    return detector(gray, sample)


def normalize_face(image, location, landmark_detector, size=112):
    landmarks = landmark_detector(image, location)

    # normalize image
    return dlib.get_face_chip(image, landmarks, size=size)


class FaceAuth:
    """

    Optimization:

    https://learnopencv.com/speeding-up-dlib-facial-landmark-detector/

    # Comparison detection:
    https://learnopencv.com/face-detection-opencv-dlib-and-deep-learning-c-python/

    """

    def __init__(self):
        # load face embeddings from file, if file exists

        try:
            with open(r"user_embedding.p", "rb") as file:
                user_backup = pickle.load(file)
                self.users = user_backup
                print("Loaded user embeddings!")
        except FileNotFoundError:
            self.users = []

        self.active = True
        self.capture = VideoStream(src=0).start()
        # self.capture = VideoStream(usePiCamera=True).start()
        self.haar_cascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.landmark_detector = dlib.shape_predictor('../models/shape_predictor_5_face_landmarks.dat')
        self.timer = None
        self.net = MobileFaceNet()
        self.detector = dlib.get_frontal_face_detector()

    def extract_faces_haar(self, image):
        """
        Extract the faces from a live video feed. If there are multiple faces, choose the nearest face.
        """

        image_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

        # extract faces with haar classifier
        face_locations = self.haar_cascade.detectMultiScale(
            image_gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(50, 50)
        )

        if len(face_locations) > 0:

            # get the biggest face
            faces_sizes = [w + h for (x, y, w, h) in face_locations]
            biggest_face_location = face_locations[faces_sizes.index(max(faces_sizes))]

            # make rectange object for dlib landmark detector
            x, y, w, h = biggest_face_location
            face_locations_dlib = dlib.rectangle(x, y, x + w, y + h)

            # normalize faces by detecting facial features
            landmarks = self.landmark_detector(image, face_locations_dlib)
            # extract, rotate and resize the image
            face_img = dlib.get_face_chip(image, landmarks, size=112, padding=0.3)

            return face_img, face_locations
        else:
            return None, []

    def extract_face_hog(self, image):
        """
        Check if there is only one face in the image, this image is used for learning a face
        """

        image_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

        # extract faces with haar classifier
        face_locations = self.detector(image_gray, 1)

        if len(face_locations) == 1:
            location = face_locations[0]
            # normalize faces by detecting facial features
            landmarks = self.landmark_detector(image, location)
            # extract, rotate and resize the image
            face_img = dlib.get_face_chip(image, landmarks, size=112, padding=0.3)
            return face_img
        else:
            return None

    def register_face(self, name, image):
        """

        :param name:
        :param image:
        :return:
        """

        # extract face
        face = self.extract_face_hog(image)

        # calculate embedding
        embedding = self.net.calculate_embedding(face)

        # append to users database
        self.users.append((name, embedding))
        # write face embeddings to pickle file
        with open(r"user_embedding.p", "wb") as file:
            pickle.dump(self.users, file)

        print(f"Registered new face for {name}")

    def match_face(self, normalized_face, tolerance=0.6):
        """

        :param image:
        :param location:
        :param tolerance:
        :return:
        """

        # calculate embedding
        unknown_embedding = self.net.calculate_embedding(normalized_face)

        distances = []
        for name, encoding in self.users:
            distances.append(distance_euclid(unknown_embedding, encoding))

        if min(distances) <= tolerance:
            return self.users[distances.index(min(distances))][0], min(distances)
        else:
            return "unknown", -1

    def stop(self):
        """

        :return:
        """

        self.active = False

    def detectAndRecognize(self, image):
        """

        :param image:
        :return:
        """

        # detect faces in image
        face, face_locations = self.extract_faces_haar(image)

        # match face to entries in database
        if face is not None:
            match = self.match_face(face)
            print(match)
            cv.imshow("face", face)

            return match, face_locations
        else:
            return None, []

    def start(self):
        """

        :return:
        """

        # main loop
        while self.active:
            start = time.time_ns()
            frame = self.capture.read()

            match, face_locations = self.detectAndRecognize(frame)

            # print(1000 * 10 ** 6 / (end - start), "fps")

            # OpenCV returns bounding box coordinates in (x, y, w, h) order
            # but we need them in (top, right, bottom, left) order, so we
            # need to do a bit of reordering
            face_locations = [(y, x + w, y + h, x) for (x, y, w, h) in face_locations]

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

        self.capture.stop()
        cv.destroyAllWindows()


def main():
    # register faces
    auth = FaceAuth()
    # ret = auth.extract_faces_haar(cv.imread("images/niklas1.jpg"))
    # print(ret)
    auth.register_face("Niklas", cv.imread("images/niklas1.jpg"))
    auth.register_face("Craig", cv.imread("images/craig1.jpg"))

    auth.start()


if __name__ == "__main__":
    main()
