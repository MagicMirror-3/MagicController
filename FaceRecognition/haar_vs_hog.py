import os

import cv2 as cv
import dlib
import time
import statistics

# setup
dirname = os.path.dirname(__file__)
path_haar_cascade = os.path.join(dirname, "model/haarcascade_frontalface_default.xml")
haar_classifier = cv.CascadeClassifier(path_haar_cascade)

detector = dlib.get_frontal_face_detector()

# load image
image = cv.imread(os.path.join(dirname, "craig1.jpg"))
image_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)


# inference

def benchmark_fct(function, n):
    timings1 = []
    for _ in range(n):
        start = time.time()
        function()
        end = time.time()

        timings1.append((end - start) * 1000)
    return statistics.mean(timings1)


def haar():
    _ = haar_classifier.detectMultiScale(
        image_gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(50, 50)
    )


def hog():
    _ = detector(image_gray, 0)


print(f"Haar: {benchmark_fct(haar, 100)} ms")
print(f"Haar: {benchmark_fct(hog, 100)} ms")
