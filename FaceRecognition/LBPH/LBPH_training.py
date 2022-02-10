import json

import dlib
import cv2 as cv
import os

import numpy as np

face_detector = dlib.get_frontal_face_detector()
landmark_detector = dlib.shape_predictor('../models/shape_predictor_5_face_landmarks.dat')

recognizer = cv.face.LBPHFaceRecognizer_create(radius=5, neighbors=8, grid_x=8, grid_y=8)


def localize_faces(image, detector, sample=0):
    return detector(image, sample)


def normalize_face(image, location, landmark_detector):
    landmarks = landmark_detector(image, location)

    # normalize image
    face_chip = dlib.get_face_chip(image, landmarks)

    return face_chip


training_images = []
training_labels = []

training_images_path = os.path.join(os.getcwd(), "training_images")
for root, dirs, files in os.walk(training_images_path):
    for file in files:  # check files in every directory
        if file.endswith("jpeg") or file.endswith("jpg") or file.endswith("png"):
            file_path = os.path.join(root, file)
            person_name = os.path.basename(root)

            print(file_path, person_name)

            image = cv.imread(file_path)

            # extract faces
            face_locations = localize_faces(image, face_detector, sample=0)

            if len(face_locations) != 1:
                print(f"Error! Detected {len(face_locations)} faces")
                continue

            norm_face = normalize_face(image, face_locations[0], landmark_detector)
            norm_face = cv.cvtColor(norm_face, cv.COLOR_BGR2GRAY)
            cv.imshow("Norm faces", norm_face)
            cv.waitKey(1)

            training_images.append(norm_face)
            training_labels.append(person_name)

print(training_labels)

# generate ids for training labels
unique_labels = list(set(training_labels))
id_by_name = dict()
name_by_id = dict()

for i, label in enumerate(unique_labels):
    print(label, ":", i)
    id_by_name[label] = i
    name_by_id[i] = label

# replace labels with id
training_labels = [id_by_name[name] for name in training_labels]

# save name_by_id
path = os.path.join(os.path.join(os.getcwd(), "training_images"), "names.json")
json.dump(name_by_id, open(path, "w"))

recognizer.train(training_images, np.array(training_labels))
recognizer.save("trained_file.yml")
