import cv2 as cv
import numpy as np

from sklearn.datasets import fetch_lfw_people

lfw_people = fetch_lfw_people(min_faces_per_person=30, resize=1.0)

for name in lfw_people.target_names:
    print(name)

counter = 0
for image in lfw_people.images:
    cv.imwrite(r"C:\Users\n-dro\OneDrive\Dokumente\GitHub\MagicController\FaceRecognition\LBPH\training_images" + r"\"" +  str(counter) + ".jpg", image)
    counter += 1
