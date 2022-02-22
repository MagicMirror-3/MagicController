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
import dlib

from FaceAuthentication import FaceAuthentication
from sklearn.metrics import classification_report


def create_dataset():
    haar_cascade = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')
    detector = dlib.get_frontal_face_detector()
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
                face_locations_haar = haar_cascade.detectMultiScale(
                    image,
                    scaleFactor=1.2,
                    minNeighbors=5,
                    minSize=(50, 50)
                )

                face_locations_hog = detector(image, 1)

                if len(face_locations_haar) != 1 or len(face_locations_hog) != 1:
                    print(f"Error! Detected 0 or more than one faces")
                    continue

                if not person_name in dataset:
                    dataset[person_name] = []

                dataset[person_name].append(image)

    return dataset


def main():
    load_from_file = True

    if load_from_file:
        with open(r"dataset.p", "rb") as file:
            master_dataset = pickle.load(file)
    else:
        master_dataset = create_dataset()
        with open(r"dataset.p", "wb") as file:
            pickle.dump(master_dataset, file)

    for key, values in master_dataset.items():
        print(key, " : ", len(master_dataset[key]))

    print("Number of people: ", len(master_dataset))
    print("\n")

    # ---------------------------------------------

    iterations = 19
    max_training_images = 5
    n_testing_images = 19

    # ---------------------------------------------

    labels = list(master_dataset.keys())

    results = []

    auth = FaceAuthentication(benchmark_mode=True)

    # ---------------------
    for n_training_images in range(1, max_training_images + 1):
        print(f" @@@@@@@@@@@@@@ {n_training_images} training images @@@@@@@@@@@@@@ ")
        big_result = []

        # reduce list size
        dataset = dict()
        for key, values in master_dataset.items():
            dataset[key] = values[:n_testing_images + n_training_images]

        # number of repeating the benchmark
        for i in range(iterations):

            print(f"################## Iteration: {i} ####################")

            test = []
            pred = []

            auth.delete_all_users()

            # shuffle all images for each iteration
            for name, images in dataset.items():
                random.shuffle(dataset[name])

            # train face recognition system with first n images
            for name, images in dataset.items():
                # pick first "n_training_images" for training
                train_images = images[:n_training_images]

                for train_image in train_images:
                    try:
                        auth.register_face(name, train_image)
                    except:
                        pass

                # remove training images from dataset
                dataset[name] = images[n_training_images:]

            # test face recognition system against whole dataset
            for name, images in dataset.items():
                for image in images:
                    match, distance, face_location = auth.match_face(image, tolerance=10)
                    print("Actual: ", name, " Predicted: ", match, " ", distance)

                    # todo: either add unknown, how to handle none?
                    if match is not None:
                        test.append(name)
                        pred.append(match)

            big_result.append(
                classification_report(test, pred, digits=4, output_dict=True)['macro avg'])
        results.append(big_result)
    print(results)


if __name__ == "__main__":
    main()
