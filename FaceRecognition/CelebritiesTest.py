import cv2 as cv
import face_recognition as fr
import numpy as np


def extract_faces(image):
    # detect faces in image
    face_locations = fr.face_locations(image, model="hog")

    faces = []
    for (y1, x2, y2, x1) in face_locations:
        faces.append(image[y1:y2, x1:x2])

    return faces


def distance_euclid(enc1, enc2):
    return np.linalg.norm(enc1 - enc2)


class FaceAuth:
    def __init__(self):
        self.users = []

    def register_face(self, name, image):
        self.users.append((name, fr.face_encodings(image)[0]))

    def match_face(self, image, tolerance=0.5):
        unknown_encoding = fr.face_encodings(image)[0]

        distances = []
        for name, encoding in self.users:
            distances.append(distance_euclid(unknown_encoding, encoding))

        if min(distances) <= tolerance:
            return self.users[distances.index(min(distances))][0], min(distances)
        else:
            return "unknown", -1


# load images for registering
r1 = cv.imread("images/known/rock1.jpg")
r2 = cv.imread("images/known/redcliffe1.jpg")
r3 = cv.imread("images/known/craig1.jpg")
auth = FaceAuth()
auth.register_face("Rock", r1)
auth.register_face("redcliffe", r2)
auth.register_face("craig", r3)

# testing data
tests = [
    ["craig", cv.imread("images/known/craig2.jpg")],
    ["craig", cv.imread("images/known/craig3.jpg")],
    ["rock", cv.imread("images/known/rock2.jpg")],
    ["rock", cv.imread("images/known/rock3.jpg")],
    ["redcliffe", cv.imread("images/known/redcliffe2.jpg")],
    ["redcliffe", cv.imread("images/known/redcliffe3.jpg")],
    ["unknown", cv.imread("images/unknown/1.jpg")],
    ["unknown", cv.imread("images/unknown/2.jpg")],
    ["unknown", cv.imread("images/unknown/3.jpg")],
    ["unknown", cv.imread("images/unknown/4.jpg")]
]

for test in tests:
    image = test[1]
    name = test[0]

    try:
        predicted_name, distance = auth.match_face(image, tolerance=0.6)
        print(f"Predicted face: {predicted_name} Actual face: {name} Distance: {distance}")
    except:
        print("error")
