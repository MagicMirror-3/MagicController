import pickle
import platform
import time

import cv2 as cv
import dlib
from imutils.video import VideoStream
import os

import numpy as np

from MobileFaceNetLite import MobileFaceNetLite
from MobileFaceNetStandard import MobileFaceNetStandard
from MirrorFaceOutput import MirrorFaceOutput

IS_RASPBERRY_PI = platform.machine() == "armv7l"


class FaceAuthentication:
    """

    Optimization:

    """

    def __init__(self, benchmark_mode=False, lite=True, resolution=(640, 480)):
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

        if IS_RASPBERRY_PI or lite:
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

        # initiate camera
        if IS_RASPBERRY_PI:
            print("Use picamera")
            self.capture = VideoStream(usePiCamera=True, resolution=resolution).start()
        else:
            print("Use USB Webcam")
            self.capture = VideoStream(src=0, resolution=resolution).start()

    def get_face_locations(self, image):
        image_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

        # extract faces with haar classifier
        face_locations = self.haar_cascade.detectMultiScale(
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

        face_locations = self.get_face_locations(image)

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

    def register_faces(self, name, images, min_number_faces):
        """

        Register multiple faces, there must be at least min_number of images, that contain identifiable faces.

        :param images:
        :param min_number_faces:
        :param name:
        :return: True, if registration was successful, False if it was not
        """

        images_rgb = [cv.cvtColor(image, cv.COLOR_BGR2RGB) for image in images]

        # select images, where exactly one face is recognized
        usable_images = []
        locations = []

        for image in images_rgb:
            # locations_in_img = self.get_face_locations(image)
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
            # locations = [self.location_tuple_to_dlib_rectangle(*location) for location in locations]

            # normalize faces based on it´s location
            for face in [self.normalize_face(face, location) for face, location in zip(usable_images, locations)]:
                # calculate embedding
                embedding = self.net.calculate_embedding(face)
                # insert into users database
                self.users.append((name, embedding))

            # write face embeddings to pickle file
            if not self.benchmark_mode:
                with open(r"user_embedding.p", "wb") as file:
                    pickle.dump(self.users, file)

            print(f"Registered {min_number_faces} faces for {name}")
            return True

        else:
            print(f"Only detected {len(usable_images)} usable images")
            return False

    @staticmethod
    def location_tuple_to_dlib_rectangle(x, y, w, h):
        return dlib.rectangle(x, y, x + w, y + h)

    def match_face(self, image, tolerance=0.65):

        """

        :param image:
        :param tolerance:
        :return:
        """

        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

        face_location = self.detect_biggest_face(image)

        if face_location is not None:
            x, y, w, h = face_location
            dlib_rectangle = self.location_tuple_to_dlib_rectangle(*face_location)

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

    def live_recognition(self):
        """

        :return:
        """

        output = MirrorFaceOutput()

        # main loop
        while self.active:

            frame = self.capture.read()

            if frame is not None:
                start = time.time()
                match, distance, face_location = self.match_face(frame, tolerance=0.65)
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
    # register faces
    auth = FaceAuthentication(benchmark_mode=True, lite=True)

    dirname = os.path.dirname(__file__)

    path_niklas1 = os.path.join(dirname, "images/niklas1.jpg")
    path_niklas2 = os.path.join(dirname, "images/niklas2.jpg")
    path_niklas3 = os.path.join(dirname, "images/niklas3.jpg")
    path_niklas4 = os.path.join(dirname, "images/niklas4.jpg")

    path_craig1 = os.path.join(dirname, "images/craig1.jpg")
    path_craig2 = os.path.join(dirname, "images/craig2.jpg")
    path_craig3 = os.path.join(dirname, "images/craig3.jpg")
    path_craig4 = os.path.join(dirname, "images/craig4.jpg")

    niklas_imgs = [
        cv.imread(path_niklas1),
        cv.imread(path_niklas2),
        cv.imread(path_niklas3),
        cv.imread(path_niklas4),
    ]

    craig_imgs = [
        cv.imread(path_craig1),
        cv.imread(path_craig2),
        cv.imread(path_craig3),
        cv.imread(path_craig4),

    ]

    print(auth.register_faces("Niklas", niklas_imgs, 4))
    print(auth.register_faces("Craig", craig_imgs, 4))

    auth.live_recognition()


if __name__ == "__main__":
    main()
