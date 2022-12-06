import os
import platform

import cv2 as cv
import dlib
import numpy as np
from loguru import logger

from .MobileFaceNet import MobileFaceNet, import_tensorflow

# import tensorflow conbditionally, use Interpreter from tflite_runtime if one is on the raspberry pi
IS_RASPBERRY_PI = platform.machine() == "armv7l"
if IS_RASPBERRY_PI:
    from tflite_runtime.interpreter import Interpreter
else:
    tf = import_tensorflow()
    Interpreter = tf.lite.Interpreter


class MobileFaceNetLite(MobileFaceNet):
    def __init__(self):
        self.interpreter = None
        self.input_details = None
        self.output_details = None

    def load_model(self, model_path):
        model_exp = os.path.expanduser(model_path)
        if os.path.isfile(model_exp):
            # Load the TFLite model and allocate tensors.
            self.interpreter = Interpreter(
                model_path=model_path, num_threads=4
            )
            self.interpreter.allocate_tensors()

            # Get input and output tensors.
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            logger.debug("Loaded MobileFaceNet model")
        else:
            logger.warning("Found no model to use.")

    def calculate_embedding(self, face_image):
        face_image = face_image.astype(np.float32)
        face_image = self.preprocess_image(face_image)

        self.interpreter.set_tensor(self.input_details[0]["index"], face_image)
        self.interpreter.invoke()
        return self.interpreter.get_tensor(self.output_details[0]["index"])


def main():
    def localize_faces(image, detector, sample=1):
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        return detector(gray, sample)

    def normalize_face(image, location, landmark_detector, size=112):
        landmarks = landmark_detector(image, location)

        # normalize image
        return dlib.get_face_chip(image, landmarks, size=size)

    def distance_euclid(enc1, enc2):
        return np.linalg.norm(enc1 - enc2)

    face_detector = dlib.get_frontal_face_detector()
    landmark_detector = dlib.shape_predictor(
        "../models/shape_predictor_5_face_landmarks.dat"
    )

    img = cv.imread("images/niklas1.jpg")
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    location = localize_faces(img, face_detector, sample=1)
    niklas1 = normalize_face(img, location[0], landmark_detector, size=112)

    img = cv.imread("images/niklas2.jpg")
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    location = localize_faces(img, face_detector, sample=1)
    niklas2 = normalize_face(img, location[0], landmark_detector, size=112)

    img = cv.imread("images/craig1.jpg")
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    location = localize_faces(img, face_detector, sample=1)
    craig1 = normalize_face(img, location[0], landmark_detector, size=112)

    img = cv.imread("images/craig2.jpg")
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    location = localize_faces(img, face_detector, sample=1)
    craig2 = normalize_face(img, location[0], landmark_detector, size=112)

    img = cv.imread("images/rock1.jpg")
    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    location = localize_faces(img, face_detector, sample=1)
    rock1 = normalize_face(img, location[0], landmark_detector, size=112)

    # init FaceNet
    net = MobileFaceNetLite()
    net.load_model("model/MobileFaceNet.tflite")
    niklas1 = net.calculate_embedding(niklas1)
    niklas2 = net.calculate_embedding(niklas2)
    craig1 = net.calculate_embedding(craig1)
    craig2 = net.calculate_embedding(craig2)
    rock1 = net.calculate_embedding(rock1)

    # calculate embeddings to test FaceNet
    print("########## Same person ##########")
    print("niklas - niklas", distance_euclid(niklas1, niklas2))
    print("craig - craig", distance_euclid(craig2, craig1))
    print("####### Different person ########")
    print("niklas1 - craig", distance_euclid(niklas1, craig1))
    print("niklas2 - craig", distance_euclid(niklas2, craig1))
    print("niklas2 - rock", distance_euclid(niklas2, rock1))
    print("craig1 - rock", distance_euclid(craig1, rock1))
    print("craig2 - rock", distance_euclid(craig2, rock1))


if __name__ == "__main__":
    main()
