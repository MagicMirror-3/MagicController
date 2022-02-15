# integrate MobileFaceNet into existing detection code

"""
https://github.com/sirius-ai/MobileFaceNet_TF/blob/master/test_nets.py

https://github.com/sirius-ai/MobileFaceNet_TF/tree/master/arch/pretrained_model

loading: https://stackoverflow.com/questions/51278213/what-is-the-use-of-a-pb-file-in-tensorflow-and-how-does-it-work


load frozen graph: https://leimao.github.io/blog/Save-Load-Inference-From-TF2-Frozen-Graph/
"""

import tensorflow as tf
import numpy as np
import time
import os
import cv2 as cv
import dlib


class MobileFaceNet:
    def __init__(self):
        tf.compat.v1.Graph().as_default()
        self.sess = tf.compat.v1.Session()
        self.load_model("model/MobileFaceNet_9925_9680.pb")
        self.inputs_placeholder = tf.compat.v1.get_default_graph().get_tensor_by_name("input:0")
        self.embeddings = tf.compat.v1.get_default_graph().get_tensor_by_name("embeddings:0")

    def load_model(self, model):
        # Check if the model is a model directory (containing a metagraph and a checkpoint file)
        #  or if it is a protobuf file with a frozen graph
        model_exp = os.path.expanduser(model)
        if os.path.isfile(model_exp):
            print('Model filename: %s' % model_exp)
            with tf.compat.v1.gfile.GFile(model_exp, 'rb') as f:
                graph_def = tf.compat.v1.GraphDef()
                graph_def.ParseFromString(f.read())
                tf.import_graph_def(graph_def, name='')
        else:
            print('Found no .pb file')

    def preprocess_image(self, img):
        """

        """

        img = img - 127.5
        img = img * 0.0078125

        return np.expand_dims(img, axis=0)

    def calculate_embedding(self, img):
        img = self.preprocess_image(img)

        # input dict
        feed_dict = {self.inputs_placeholder: img}

        start = time.time_ns()
        out = self.sess.run(self.embeddings, feed_dict=feed_dict)
        end = time.time_ns()
        # print((end - start) / 10 ** 6, "ms")
        # print(out)

        return out


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
    landmark_detector = dlib.shape_predictor('../models/shape_predictor_5_face_landmarks.dat')

    img = cv.imread("images/niklas1.jpg")
    location = localize_faces(img, face_detector, sample=1)
    niklas1 = normalize_face(img, location[0], landmark_detector, size=112)

    img = cv.imread("images/niklas2.jpg")
    location = localize_faces(img, face_detector, sample=1)
    niklas2 = normalize_face(img, location[0], landmark_detector, size=112)

    img = cv.imread("images/craig1.jpg")
    location = localize_faces(img, face_detector, sample=1)
    craig1 = normalize_face(img, location[0], landmark_detector, size=112)

    img = cv.imread("images/craig2.jpg")
    location = localize_faces(img, face_detector, sample=1)
    craig2 = normalize_face(img, location[0], landmark_detector, size=112)

    img = cv.imread("images/rock1.jpg")
    location = localize_faces(img, face_detector, sample=1)
    rock1 = normalize_face(img, location[0], landmark_detector, size=112)

    # init FaceNet
    net = MobileFaceNet()
    niklas1 = net.calculate_embedding(niklas1)
    niklas2 = net.calculate_embedding(niklas2)
    craig1 = net.calculate_embedding(craig1)
    craig2 = net.calculate_embedding(craig2)
    rock1 = net.calculate_embedding(rock1)

    # calculate embeddings to test FaceNet
    print("niklas - niklas", distance_euclid(niklas1, niklas2))
    print("craig - craig", distance_euclid(craig2, craig1))
    print("niklas1 - craig", distance_euclid(niklas1, craig1))
    print("niklas2 - craig", distance_euclid(niklas2, craig1))
    print("niklas2 - rock", distance_euclid(niklas2, rock1))
    print("craig1 - rock", distance_euclid(craig1, rock1))
    print("craig2 - rock", distance_euclid(craig2, rock1))


if __name__ == '__main__':
    main()
