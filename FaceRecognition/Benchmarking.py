import cv2 as cv
import imutils
from deepface import DeepFace
import face_recognition as fr
import time

"""
This script benchmarks the performance of facial embedding using various models
"""

image = cv.imread("images/known/craig1.jpg")
models = ["VGG-Face", "Facenet", "Facenet512", "OpenFace", "DeepID", "ArcFace", "Dlib"]

# preprocessing image
image_processed = imutils.resize(image, width=500)

for model in models:
    start = time.time()
    embedding = DeepFace.represent(img_path=image_processed, model_name=model)
    end = time.time()
    print(f"{model} took {round(end-start, 4)} s")


"""
Results: (base image)

VGG-Face took 1.308 s
Facenet took 2.488 s
Facenet512 took 2.478 s
OpenFace took 1.075 s
DeepFace took 21.025 s
DeepID took 0.199 s
ArcFace took 1.429 s
Dlib took 0.466 s

Results: (scaled)
VGG-Face took 1.211 s
Facenet took 2.45 s
Facenet512 took 2.441 s
OpenFace took 1.034 s
DeepID took 0.137 s
ArcFace took 1.366 s
Dlib took 0.415 s

"""
