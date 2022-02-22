import time

from FaceAuthentication import FaceAuthentication
import os
import cv2 as cv
import statistics

dirname = os.path.dirname(__file__)
path_niklas = os.path.join(dirname, "images/niklas1.jpg")
path_craig = os.path.join(dirname, "images/craig1.jpg")
print("path niklas", path_niklas)
print("path craig", path_craig)

niklas = cv.imread(path_niklas)
print("image niklas", niklas)
craig = cv.imread(path_craig)
print("image craig", craig)

print("equal", niklas == craig)

auth = FaceAuthentication(benchmark_mode=True)
print("Started authentication")
auth.register_face("Niklas", niklas)
print("Registered Niklas")
auth.register_face("Craig", craig)
print("Registered Craig")

fps_list = []
for i in range(2):

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
