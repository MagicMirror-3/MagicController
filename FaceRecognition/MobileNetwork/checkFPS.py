import time

from FaceAuthentication import FaceAuthentication
import os
import cv2 as cv
import statistics

auth = FaceAuthentication()

dirname = os.path.dirname(__file__)

path_niklas = os.path.join(dirname, "images/niklas1.jpg")
path_craig = os.path.join(dirname, "images/craig1.jpg")

niklas = cv.imread(path_niklas)
craig = cv.imread(path_craig)

auth.register_face("Niklas", cv.imread(niklas))
auth.register_face("Craig", cv.imread(craig))

distances = []
for _ in range(30):

    start = time.time()
    match, distance, face_location = auth.match_face(niklas)
    end = time.time()
    if match is not None and distance is not None:
        print(f"Identified {match}, Dist: {round(distance, 4)}, FPS: {1 / (end - start)}")
        distances.append(distance)
    else:
        print("No match")

print(f"Average FPS: {statistics.mean(distances)}")

