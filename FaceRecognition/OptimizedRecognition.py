import cv2 as cv
import time
import face_recognition as fr
import imutils

import numpy as np


def distance_euclid(enc1, enc2):
    return np.linalg.norm(enc1 - enc2)


class FaceAuth:
    def __init__(self):
        self.users = []

    def register_face(self, name, image):
        # multiple ?
        self.users.append((name, fr.face_encodings(image)[0]))

    def match_face(self, image, location, tolerance=0.5):
        unknown_encoding = fr.face_encodings(image, known_face_locations=[location])[0]

        distances = []
        for name, encoding in self.users:
            distances.append(distance_euclid(unknown_encoding, encoding))

        if min(distances) <= tolerance:
            return self.users[distances.index(min(distances))][0], min(distances)
        else:
            return "unknown", -1


# -----------------------------------------------------------------------------------

capture = cv.VideoCapture(0)
face_detector = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')

number_faces_last_frame = 0

# register faces
auth = FaceAuth()
auth.register_face("Niklas", cv.imread("images/known/Niklas.jpg"))
auth.register_face("Craig", cv.imread("images/known/craig1.jpg"))

while True:
    isTrue, frame = capture.read()
    start = time.time()

    # scale image down
    frame = imutils.resize(frame, width=500)

    frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    # ---------------------------

    # detect faces in image
    face_locations = face_detector.detectMultiScale(frame_gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
    # OpenCV returns bounding box coordinates in (x, y, w, h) order
    # but we need them in (top, right, bottom, left) order, so we
    # need to do a bit of reordering
    face_locations = [(y, x + w, y + h, x) for (x, y, w, h) in face_locations]

    # only check identity if number of faces has changed compared to last frame
    if number_faces_last_frame != len(face_locations):

        # when there are multiple faces, only identify the first one
        for face_location in face_locations:

            # identify face
            name = auth.match_face(frame_rgb, location=face_location)

            if name != ('unknown', -1):
                print(f"Identified: {name}")
                number_faces_last_frame = len(face_locations)
                break
        else:
            # no faces detected
            number_faces_last_frame = len(face_locations)

    # draw rectangles for faces
    for f1, f2, f3, f4 in face_locations:
        frame_gray = cv.rectangle(frame, (f2, f1), (f4, f3), (255, 0, 0), 3)

    # extract faces from image
    # for (y1, x2, y2, x1) in face_locations:
    # face = frame[y1:y2, x1:x2]
    # cv.imshow("face", face)
    # ---------------------------
    end = time.time()
    # print(face_locations, " fps: ", round(1 / (end - start), 1))

    cv.imshow('Video', frame)
    if cv.waitKey(20) & 0xFF == ord('d'):
        break

capture.release()
cv.destroyAllWindows()
