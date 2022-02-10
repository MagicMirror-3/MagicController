from imutils import face_utils
import numpy as np
import imutils
import dlib
import cv2

face_detector = dlib.get_frontal_face_detector()
landmark_detector = dlib.shape_predictor('models/shape_predictor_68_face_landmarks.dat')
facerec = dlib.face_recognition_model_v1("models/dlib_face_recognition_resnet_model_v1.dat")
cam = cv2.VideoCapture(0)

while True:
    ret, image = cam.read()
    if ret:
        image = imutils.resize(image, width=500)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        rects = face_detector(gray, 1)
        for (i, rect) in enumerate(rects):

            # detect landmarks
            landmarks = landmark_detector(gray, rect)

            # draw rectangle to window
            (x, y, w, h) = face_utils.rect_to_bb(rect)
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(image, f"Face {i + 1}", (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # normalize image
            face_chip = dlib.get_face_chip(image, landmarks)

            # calculate embedding
            # face_descriptor_from_prealigned_image = facerec.compute_face_descriptor(face_chip)

            cv2.imshow("Normalized", face_chip)

            # draw landmarks
            landmarks = face_utils.shape_to_np(landmarks)  # convert to np array
            for (x, y) in landmarks:
                cv2.circle(image, (x, y), 1, (0, 0, 255), 2)

        cv2.imshow('Live feed', image)

    if cv2.waitKey(1) == 27:
        break
cam.release()
cv2.destroyAllWindows()
