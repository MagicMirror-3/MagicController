import os

import cv2 as cv
import numpy as np
from sklearn.datasets import fetch_lfw_people

faces_per_person = 35
number_of_people = 20

lfw_people = fetch_lfw_people(
    min_faces_per_person=faces_per_person,
    resize=2.0,
    funneled=False,
    slice_=None,
    color=True,
)

new_directory = os.path.join(os.getcwd(), "benchmark_images")
try:
    os.mkdir(new_directory)
except:
    pass

people_ids = np.array(lfw_people.target)
images = lfw_people.images

for person_id in range(number_of_people):
    person_name = lfw_people.target_names[person_id]
    path = os.path.join(os.getcwd(), "benchmark_images")
    path = os.path.join(path, person_name)
    os.mkdir(path)

    images_for_id = images[people_ids == person_id]
    images_for_id = images_for_id[0:faces_per_person]

    for number, image in enumerate(images_for_id):
        image_path = os.path.join(path, f"{number}.jpg")
        cv.imwrite(image_path, image)

# take 30 images of 5 persons, from each person in one folder
