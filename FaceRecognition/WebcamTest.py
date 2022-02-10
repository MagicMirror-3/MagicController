import cv2 as cv
import face_recognition as fr
import time
import numpy as np


# installation (Windows) on python 3.8
# - install VS C++ Compiler Tools
# - make venv
# - pip install cmake dlib face_recognition

# Development Steps

# test for package face_recognition and own implementation with opencv and FaceNet
# benchmark these options on the raspberry pi

# also try haar classifier

# 1: Take Webcam image
# 2: detect own face
# 3: extract Face embeddings
# 4: Try to match own faces

# Detection
DLIB = False
Haar = True

# Recognition
DLIB_REC = True

capture = cv.VideoCapture(0)
encoding_old = []
face_detector = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')

while True:
    isTrue, frame = capture.read()
    start = time.time()
    # ---------------------------

    face_locations = []

    # detect faces in image
    if DLIB:
        face_locations = fr.face_locations(frame, model="hog")
    elif Haar:
        face_locations = face_detector.detectMultiScale(frame, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))
        face_locations = [(y, x + w, y + h, x) for (x, y, w, h) in face_locations]

    # draw rectangles for faces
    for f1, f2, f3, f4 in face_locations:
        frame = cv.rectangle(frame, (f2, f1), (f4, f3), (255, 0, 0), 3)

    # extract faces from image
    if DLIB_REC:
        # for (y1, x2, y2, x1) in face_locations:
            # face = frame[y1:y2, x1:x2]
        encodings = fr.face_encodings(frame, known_face_locations=face_locations)

        for encoding in encodings:
            if encoding_old:
                # calculate euclidean distance to last frame
                print(np.linalg.norm(encoding - encoding_old[0]))
        encoding_old = encodings
                # cv.imshow("face", face)

    # ---------------------------
    end = time.time()
    print(face_locations, " fps: ", round(1 / (end - start), 1))

    cv.imshow('Video', frame)
    if cv.waitKey(20) & 0xFF == ord('d'):
        break

capture.release()
cv.destroyAllWindows()
