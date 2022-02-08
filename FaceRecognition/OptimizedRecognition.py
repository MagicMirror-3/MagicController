import cv2 as cv
import time
import face_recognition as fr
import imutils
from threading import Timer

import numpy as np


def distance_euclid(enc1, enc2):
    return np.linalg.norm(enc1 - enc2)


class FaceAuth:
    def __init__(self):
        self.users = []

    def register_face(self, name, image):
        # use first face it can find
        self.users.append((name, fr.face_encodings(image)[0]))

    def match_face(self, image, location, tolerance=0.55):
        unknown_encoding = fr.face_encodings(image, known_face_locations=[location])[0]

        distances = []
        for name, encoding in self.users:
            distances.append(distance_euclid(unknown_encoding, encoding))

        if min(distances) <= tolerance:
            return self.users[distances.index(min(distances))][0], min(distances)
        else:
            return "unknown", -1


class MirrorFaceOutput:
    def __init__(self):
        self.recognized_faces = dict()
        self.timeout = 5
        self.current_identified_user = None

    def face_detected(self, user_name):
        if user_name != self.current_identified_user:
            print(f"Identified: {user_name}")

            # if the current user is not None, the timers have to be stopped
            if self.current_identified_user is not None:
                # new face detected, stop all ongoing timers
                for _, timer in self.recognized_faces.items():
                    timer.cancel()

                # clear dictionary
                self.recognized_faces.clear()

            # set new detected user
            self.current_identified_user = user_name

        # check if a timer is already in the dictionary
        if user_name in self.recognized_faces:
            # stop timer
            self.recognized_faces[user_name].cancel()
        # create a new timer
        self.recognized_faces[user_name] = Timer(self.timeout, self.face_timeout, args=[user_name])

    def no_faces(self):
        # start timer(s) for each face, when no face is detected
        for user, timer in self.recognized_faces.items():
            try:
                timer.start()
            except:
                pass

    def face_timeout(self, user):
        # face no longer detected
        print(f"Face from {user} no longer detected")
        self.recognized_faces.pop(user)
        self.current_identified_user = None


# -----------------------------------------------------------------------------------

def detected_unknown_face():
    global detect_anyways
    detect_anyways = False


capture = cv.VideoCapture(0)
face_detector = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')

buffer_size = 50
face_count_buffer = [0] * buffer_size
last_number_faces = 0

detect_anyways = False
timer = None

output = MirrorFaceOutput()

# register faces
auth = FaceAuth()
auth.register_face("Niklas", cv.imread("images/test/Niklas.jpg"))
auth.register_face("Craig", cv.imread("images/known/craig1.jpg"))

while True:
    isTrue, frame = capture.read()
    start = time.time()

    # scale image down
    # frame = imutils.resize(frame, width=500)

    frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    # ---------------------------

    # detect faces in image
    face_locations = face_detector.detectMultiScale(frame_gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
    # OpenCV returns bounding box coordinates in (x, y, w, h) order
    # but we need them in (top, right, bottom, left) order, so we
    # need to do a bit of reordering
    face_locations = [(y, x + w, y + h, x) for (x, y, w, h) in face_locations]

    # buffer number of faces
    face_count_buffer.append(len(face_locations))
    face_count_buffer.pop(0)
    # number of faces is maximum occurring number in last x frames
    number_of_faces = max(face_count_buffer, key=face_count_buffer.count)

    # only check identity if number of faces has changed in last X frames or the detect_anyways flag is set
    if number_of_faces != last_number_faces or detect_anyways:
        detect_anyways = False
        if number_of_faces != 0:
            # when there are multiple faces, only identify the first one, if this is unknown, identify the second one.
            for face_location in face_locations:
                # identify face
                name = auth.match_face(frame_rgb, location=face_location)
                if name != ('unknown', -1):
                    # output to mirror
                    output.face_detected(name[0])

                    last_number_faces = number_of_faces
                    break

            last_number_faces = number_of_faces

            # no faces identified, after x seconds, identify again, even if number of faces doesn´t change
            if not timer is None and not timer.is_alive():
                timer = Timer(2, detected_unknown_face)
                timer.start()
        else:
            # no faces have been detected
            last_number_faces = number_of_faces
            output.no_faces() # todo: auch noch nach oben ?

    # draw rectangles for faces
    for f1, f2, f3, f4 in face_locations:
        frame_gray = cv.rectangle(frame, (f2, f1), (f4, f3), (255, 0, 0), 3)

    # extract faces from image
    # for (y1, x2, y2, x1) in face_locations:
    # face = frame[y1:y2, x1:x2]
    # cv.imshow("face", face)
    # ---------------------------
    end = time.time()

    cv.imshow('Video', frame)
    if cv.waitKey(20) & 0xFF == ord('d'):
        break

capture.release()
cv.destroyAllWindows()
