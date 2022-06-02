import pickle
import platform
import time
from threading import Thread

import cv2 as cv
import dlib
from imutils.video import VideoStream
import os

import numpy as np

from FaceRecognition.MobileFaceNetLite import MobileFaceNetLite
from FaceRecognition.MobileFaceNetStandard import MobileFaceNetStandard
from FaceRecognition.MirrorFaceOutput import MirrorFaceOutput

IS_RASPBERRY_PI = platform.machine() == "armv7l"


class FaceAuthentication:
    """

    Optimization:

    """

    def __init__(self, benchmark_mode=False, lite=True, threshold=0.8, resolution=(640, 480), mediator=None):
        # load face embeddings from file, if file exists and benchmark mode is turned off

        self.benchmark_mode = benchmark_mode
        self.threshold = threshold

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
        path_haar_cascade = os.path.join(dirname, "model/haarcascade_frontalface_default.xml")

        if IS_RASPBERRY_PI or lite:
            self.net = MobileFaceNetLite()
            path_mobile_face_net = os.path.join(dirname, "model/MobileFaceNet.tflite")
            self.net.load_model(path_mobile_face_net)
        else:
            self.net = MobileFaceNetStandard()
            path_standard_face_net = os.path.join(dirname, "model/MobileFaceNet.pb")
            self.net.load_model(path_standard_face_net)

        self.active = True
        self.haar_cascade_matching = cv.CascadeClassifier(path_haar_cascade)
        self.haar_cascade_registration = cv.CascadeClassifier(path_haar_cascade)
        self.landmark_detector = dlib.shape_predictor(path_shape_predictor)
        self.detector = dlib.get_frontal_face_detector()

        # initiate camera
        if IS_RASPBERRY_PI:
            print("Use picamera")
            self.capture = VideoStream(usePiCamera=True, resolution=resolution).start()
        else:
            print("Use USB Webcam")
            self.capture = VideoStream(src=0, resolution=resolution).start()

        self.mediator = mediator

        # threading
        self.thread = Thread(target=self.run, name="FaceAuthentication")
        self.thread.start()

    def get_face_locations(self, image, haar_classifier):
        image_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

        # extract faces with haar classifier
        face_locations = haar_classifier.detectMultiScale(
            image_gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(50, 50)
        )

        return face_locations

    def detect_biggest_face(self, image):
        """
        Extract the location of the biggest face from an image.
        If there are multiple faces, choose the nearest (biggest) face.

        Format: (x, y, w, h)

        """

        face_locations = self.get_face_locations(image, self.haar_cascade_matching)

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
        return self.detector(image_gray, 0)

    def register_faces(self, name, images, min_number_faces=1, mode='fast'):
        """

        Register multiple faces, there must be at least min_number of images, that contain identifiable faces.

        :param mode:
        :param images:
        :param min_number_faces:
        :param name:
        :return: True, if registration was successful, False if it was not
        """

        self.active = False

        FAST = mode == 'fast'

        images_rgb = [cv.cvtColor(image, cv.COLOR_BGR2RGB) for image in images]

        # select images, where exactly one face is recognized
        usable_images = []
        locations = []

        # An image is usable, if exactly one face is detected
        for image in images_rgb:
            if FAST:
                locations_in_img = self.get_face_locations(image, self.haar_cascade_registration)
            else:
                locations_in_img = self.extract_faces_hog(image)

            if len(locations_in_img) == 1:
                usable_images.append(image)
                locations.append(locations_in_img[0])

        # only proceed, if "min_number_faces" images have exactly one face
        if len(usable_images) >= min_number_faces:
            # pick the first "min_number_faces" images
            usable_images = usable_images[:min_number_faces]
            locations = locations[:min_number_faces]

            # convert location from tuple to dlib rectangle
            if FAST:
                locations = [self.location_tuple_to_dlib_rectangle(*location) for location in locations]

            # normalize faces based on it´s location
            for face in [self.normalize_face(face, location) for face, location in zip(usable_images, locations)]:
                # calculate embedding
                embedding = self.net.calculate_embedding(face)
                # insert into users database
                self.users.append((name, embedding))

            # persist face embeddings in pickle file
            if not self.benchmark_mode:
                with open(r"user_embedding.p", "wb") as file:
                    pickle.dump(self.users, file)

            print(f"Registered {min_number_faces} faces for {name}")
            self.active = True
            return True

        else:
            print(f"Only detected {len(usable_images)} usable images")
            self.active = True
            return False

    @staticmethod
    def location_tuple_to_dlib_rectangle(x, y, w, h):
        return dlib.rectangle(x, y, x + w, y + h)

    def match_face(self, image):

        """

        :param image:
        :return:
        """

        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

        face_location = self.detect_biggest_face(image)

        if face_location is not None:

            # when no users are registered, don´t calculate the embedding for a face
            if len(self.users) == 0:
                return None, None, [face_location]

            x, y, w, h = face_location
            dlib_rectangle = self.location_tuple_to_dlib_rectangle(*face_location)

            normalized_face = self.normalize_face(image, dlib_rectangle, size=112, padding=0.3)

            # calculate embedding
            unknown_embedding = self.net.calculate_embedding(normalized_face)

            distances = []
            for name, encoding in self.users:
                distances.append(self.distance_euclid(unknown_embedding, encoding))

            if min(distances) <= self.threshold:
                return self.users[distances.index(min(distances))][0], min(distances), [face_location]
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

    def normalize_face(self, image, location, size=112, padding=0.25):
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

    def delete_user(self, name):
        """
        Remove user from memory and pickle file

        :param name:
        :return:
        """
        for index, (username, _) in enumerate(self.users):
            if username == name:
                self.users.pop(index)
                break
        print("removed user")
        # also save changes in pickle file
        if not self.benchmark_mode:
            with open(r"user_embedding.p", "wb") as file:
                pickle.dump(self.users, file)

    def run(self):
        """

        :return:
        """

        output = MirrorFaceOutput(self.mediator)

        # main loop
        while True:
            if self.active:

                frame = self.capture.read()

                if frame is not None:
                    start = time.time()
                    match, distance, face_location = self.match_face(frame)
                    end = time.time()
                    if match is not None and distance is not None:
                        print(f"Identified {match}, Dist: {round(distance, 4)}, FPS: {1 / (end - start)}")

                        output.face_detected(match)

                    # OpenCV returns bounding box coordinates in (x, y, w, h) order
                    # but we need them in (top, right, bottom, left) order, so we
                    # need to do a bit of reordering
                    else:
                        output.no_faces()

                    if face_location is not None:
                        face_location = [(y, x + w, y + h, x) for (x, y, w, h) in face_location]

                        # draw rectangles for faces
                        for f1, f2, f3, f4 in face_location:
                            frame = cv.rectangle(frame, (f2, f1), (f4, f3), (255, 0, 0), 3)

                    if not IS_RASPBERRY_PI:
                        cv.imshow('Video', frame)
                        if cv.waitKey(20) & 0xFF == ord('d'):
                            break
            else:
                pass

        self.capture.stop()
        if not IS_RASPBERRY_PI:
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

    print(os.path.abspath('model/haarcascade_frontalface_default.xml'))


if __name__ == "__main__":
    main()
