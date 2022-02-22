import time

from FaceAuthentication import FaceAuthentication
import os
import cv2 as cv
import statistics

dirname = os.path.dirname(__file__)
path_niklas = os.path.join(dirname, "images/niklas1.jpg")
path_craig = os.path.join(dirname, "images/craig1.jpg")

niklas = cv.imread(path_niklas)
craig = cv.imread(path_craig)

auth = FaceAuthentication(benchmark_mode=True)
auth.register_face("Niklas", niklas)
auth.register_face("Craig", craig)

fps_list = []
for _ in range(30):

    start = time.time()
    match, distance, face_location = auth.match_face(niklas)
    end = time.time()
    if match is not None and distance is not None:
        fps = 1 / (end - start)
        print(f"Identified {match}, Dist: {round(distance, 4)}, FPS: {fps}")
        fps_list.append(fps)
    else:
        print("No match")

print(f"Average FPS: {statistics.mean(fps_list)}")

