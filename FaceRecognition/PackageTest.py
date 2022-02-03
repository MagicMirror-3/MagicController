import cv2 as cv
import face_recognition as fr
import time

# installation (Windows) on python 3.8
# - install VS C++ Compiler Tools
# - make venv
# - pip install cmake dlib face_recognition

# Development Steps

# test for package face_recognition and own implementation with opencv and FaceNet
# benchmark these options on the raspberry pi

# 1: Take Webcam image
# 2: detect own face
# 3: extract Face embeddings
# 4: Try to match own faces

capture = cv.VideoCapture(0)

while True:
    isTrue, frame = capture.read()
    start = time.time()
    # ---------------------------

    # detect faces in image
    face_locations = fr.face_locations(frame, model="hog")

    # draw rectangles for faces
    for f1, f2, f3, f4 in face_locations:
        frame = cv.rectangle(frame, (f2, f1), (f4, f3), (255, 0, 0), 3)

    # extract faces from image
    for (y1, x2, y2, x1) in face_locations:
        face = frame[y1:y2, x1:x2]
        encoding = fr.face_encodings(face, known_face_locations=face_locations)
        print(encoding)
        cv.imshow("face", face)

    # ---------------------------
    end = time.time()
    print(face_locations, " fps: ", round(1 / (end - start), 1))

    cv.imshow('Video', frame)
    if cv.waitKey(20) & 0xFF == ord('d'):
        break

capture.release()
cv.destroyAllWindows()
