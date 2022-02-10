import json
import os
import time

from imutils import face_utils
import numpy as np
import imutils
import dlib
import cv2 as cv

face_detector = dlib.get_frontal_face_detector()
landmark_detector = dlib.shape_predictor('../models/shape_predictor_5_face_landmarks.dat')
recognizer = cv.face.LBPHFaceRecognizer_create()
recognizer.read("trained_file.yml")

path = os.path.join(os.path.join(os.getcwd(), "training_images"), "names.json")
id_to_names = dict(json.load(open(path, "r")))

cam = cv.VideoCapture(0)

while True:
    ret, image = cam.read()
    if ret:
        # image = imutils.resize(image, width=800)
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

        locations = face_detector(gray, 0)
        for location in locations:

            # detect landmarks
            landmarks = landmark_detector(gray, location)

            # normalize image
            norm_face = dlib.get_face_chip(image, landmarks)
            norm_face = cv.cvtColor(norm_face, cv.COLOR_BGR2GRAY)

            # detect faces with LBPH
            start = time.time_ns()
            id_, conf = recognizer.predict(norm_face)
            end = time.time_ns()

            print((end - start) / 10 ** 6, "ms")

            if conf < 1000:
                person_name = id_to_names[str(id_)]
            else:
                person_name = "Unknown"

            # draw rectangle to window
            (x, y, w, h) = face_utils.rect_to_bb(location)
            cv.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv.putText(image, f"{person_name}, {round(conf, 2)}", (x - 10, y - 10), cv.FONT_HERSHEY_SIMPLEX, 1,
                       (0, 255, 0), 2)

            # draw landmarks
            landmarks = face_utils.shape_to_np(landmarks)  # convert to np array
            for (x, y) in landmarks:
                cv.circle(image, (x, y), 1, (0, 0, 255), 2)

        cv.imshow('Live feed', image)

    if cv.waitKey(1) == 27:
        break
cam.release()
cv.destroyAllWindows()
