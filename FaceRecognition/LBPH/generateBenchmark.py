import cv2 as cv
import numpy as np
import os

from sklearn.datasets import fetch_lfw_people

faces_per_person = 30
number_of_people = 10

lfw_people = fetch_lfw_people(min_faces_per_person=faces_per_person, resize=2.0, funneled=False, slice_=None)

new_directory = os.path.join(os.getcwd(), "training_images")
os.mkdir(new_directory)

people_ids = np.array(lfw_people.target)
images = lfw_people.images

for person_id in range(number_of_people):
    person_name = lfw_people.target_names[person_id]
    path = os.path.join(os.getcwd(), "training_images")
    path = os.path.join(path, person_name)
    os.mkdir(path)

    images_for_id = images[people_ids == person_id]
    images_for_id = images_for_id[0:faces_per_person]

    for number, image in enumerate(images_for_id):
        image_path = os.path.join(path, f"{number}.jpg")
        cv.imwrite(image_path, image)

# take 30 images of 5 persons, from each person in one folder
