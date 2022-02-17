"""
Metrics:

capture:
predicted / actual for all measurements

TP:
FP:
TN:
FN:


-------------------------
25 images of ten people

split train / test set
20 test images / 1-5 train images --> randomly choose the images that should be used for training for each person

test 1: one training image

test 2: increase number of images to train (1-5), leave number of testing data constant
    - How does cross validation look like here?

test 3: test X random people, that have not been trained with in a combined dataset of all testing images
maybe 50/50 ?

- analyze the thresholds of true positives and false negatives
- include a counter, how many images were not able to be identified
    - while submitting
    - with haar

--------

dataset structure:

{
    "dude1": [img1, img2, ...],
    "dude2": [img1, img2, ...],
    ...
}

creation:
check number of faces (haar), take up to X images

"""


import os
import pickle
import random

import cv2 as cv

from FaceAuthentication import FaceAuthentication
from sklearn.metrics import classification_report


def create_dataset():
    haar_cascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')
    dataset = dict()

    training_images_path = os.path.join(os.getcwd(), "benchmark_images")
    for root, dirs, files in os.walk(training_images_path):
        for file in files:  # check files in every directory
            if file.endswith("jpeg") or file.endswith("jpg") or file.endswith("png"):
                file_path = os.path.join(root, file)
                person_name = os.path.basename(root)

                print(file_path, person_name)

                image = cv.imread(file_path)
                image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

                # extract faces
                face_locations = haar_cascade.detectMultiScale(
                    image,
                    scaleFactor=1.2,
                    minNeighbors=5,
                    minSize=(60, 60)
                )  # draw rectangles for faces

                face_locations = [(y, x + w, y + h, x) for (x, y, w, h) in face_locations]
                for f1, f2, f3, f4 in face_locations:
                    image = cv.rectangle(image, (f2, f1), (f4, f3), (255, 0, 0), 3)
                cv.imshow("Face", image)
                cv.waitKey(1)

                if len(face_locations) != 1:
                    print(f"Error! Detected {len(face_locations)} faces")
                    continue

                if not person_name in dataset:
                    dataset[person_name] = []

                dataset[person_name].append(image)

    return dataset


def main():
    load_from_file = True

    if load_from_file:
        with open(r"dataset.p", "rb") as file:
            dataset = pickle.load(file)
    else:
        dataset = create_dataset()
        with open(r"dataset.p", "wb") as file:
            pickle.dump(dataset, file)

    print("Number of people: ", len(dataset))
    print("\n")

    # ---------------------------------------------

    iterations = 1
    n_training_images = 1
    n_testing_images = 20

    # ---------------------------------------------

    # reduce list size
    for key, values in dataset.items():
        dataset[key] = values[:n_testing_images + n_training_images]
        print(dataset[key])

    test = []
    pred = []
    labels = list(dataset.keys())

    # number of repeating the benchmark
    for i in range(iterations):

        # shuffle all images for each iteration
        for name, images in dataset.items():
            random.shuffle(dataset[name])

        auth = FaceAuthentication(benchmark_mode=True)

        # train face recognition system with first n images
        for name, images in dataset.items():
            # pick first "n_training_images" for training
            train_images = images[:n_training_images]

            for train_image in train_images:
                auth.register_face(name, train_image)

            # remove training images from dataset
            dataset[name] = images[n_training_images:]

        # test face recognition system against whole dataset
        for name, images in dataset.items():
            for image in images:
                (match, dist), _ = auth.detectAndRecognize(image, tolerance=10)
                print("Actual: ", name, " Predicted: ", match, " ", dist)

                # todo: either add unknown, how to handle none?
                if match is not None:
                    test.append(name)
                    pred.append(match)

    print("\n")
    print(classification_report(test, pred, target_names=labels, digits=4, output_dict=True))


if __name__ == "__main__":
    main()
