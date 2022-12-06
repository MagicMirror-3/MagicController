import os
import statistics
import time

import cv2 as cv
from FaceAuthentication import FaceAuthentication

dirname = os.path.dirname(__file__)

path_niklas = os.path.join(dirname, "images/niklas2.jpg")
path_craig = os.path.join(dirname, "images/craig1.jpg")
print("path niklas", path_niklas)
print("path craig", path_craig)

niklas = cv.imread(path_niklas)
craig = cv.imread(path_craig)

auth = FaceAuthentication(benchmark_mode=True, lite=True)

auth.register_faces("Craig", [craig], 1)
auth.register_faces("Niklas", [niklas], 1)

actual_face = niklas

fps_list = []

match, distance, face_location = auth.match_face(actual_face)
for i in range(40):
    print("------------------------------------------")
    start = time.time()
    match, distance, face_location = auth.match_face(actual_face)
    end = time.time()
    if match is not None and distance is not None:
        fps = 1 / (end - start)
        print(f"Identified {match}, Dist: {round(distance, 4)}, FPS: {fps}")
        fps_list.append(fps)
    else:
        print("No match")

print(f"Average FPS: {statistics.mean(fps_list)}")
