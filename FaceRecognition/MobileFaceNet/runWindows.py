"""
https://github.com/sirius-ai/MobileFaceNet_TF/blob/master/test_nets.py
"""

import tensorflow as tf
import numpy as np
import time
import os
import cv2 as cv
import dlib

# ----------------------- cv -------------------------------

face_detector = dlib.get_frontal_face_detector()
landmark_detector = dlib.shape_predictor('../models/shape_predictor_5_face_landmarks.dat')


def load_image(img_path):
    img = cv.imread(img_path)
    # img = cv.cvtColor(img, cv.COLOR_BGR2RGB)

    location = localize_faces(img, face_detector, sample=1)
    print(location) # Index !!!!
    face_img = normalize_face(img, location[0], landmark_detector)

    face_img = face_img - 127.5
    face_img = face_img * 0.0078125

    return face_img


def localize_faces(image, detector, sample=1):
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    return detector(gray, sample)


def normalize_face(image, location, landmark_detector, size=112):
    landmarks = landmark_detector(image, location)

    # normalize image
    return dlib.get_face_chip(image, landmarks, size=size)


# ----------------------- tensorflow -------------------------------

def load_model(model):
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


def main():
    with tf.compat.v1.Graph().as_default():
        with tf.compat.v1.Session() as sess:
            # load image data
            image = load_image("../LBPH/training_images/Niklas/WIN_20220211_00_07_52_Pro.jpg")

            # make dimension to (1,112,112,3)
            image = np.expand_dims(image, axis=0)

            # Load the model
            load_model("model/MobileFaceNet_9925_9680.pb")

            # Get input and output tensors, ignore phase_train_placeholder for it have default value.
            inputs_placeholder = tf.compat.v1.get_default_graph().get_tensor_by_name("input:0")
            embeddings = tf.compat.v1.get_default_graph().get_tensor_by_name("embeddings:0")

            feed_dict = {inputs_placeholder: image}

            out = sess.run(embeddings, feed_dict=feed_dict)

            start = time.time_ns()
            out = sess.run(embeddings, feed_dict=feed_dict)
            end = time.time_ns()
            print((end - start) / 10 ** 6, "ms")
            print(out)


if __name__ == '__main__':
    main()
