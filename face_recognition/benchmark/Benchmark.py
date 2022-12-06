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

---------------------------------------

Important: Check performance of images taken with pi camera vs with webcam/ smartphone camera

Check knn vs k means vs basic approach vs median

"""

import os
import pickle
import random

import cv2 as cv
import dlib
import pandas as pd
from FaceAuthentication import FaceAuthentication


def create_dataset():
    haar_cascade = cv.CascadeClassifier(
        cv.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    detector = dlib.get_frontal_face_detector()
    dataset = dict()

    training_images_path = os.path.join(os.getcwd(), "benchmark_images")
    for root, dirs, files in os.walk(training_images_path):
        for file in files:  # check files in every directory
            if (
                file.endswith("jpeg")
                or file.endswith("jpg")
                or file.endswith("png")
            ):
                file_path = os.path.join(root, file)
                person_name = os.path.basename(root)

                print(file_path, person_name)

                image = cv.imread(file_path)
                image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

                # extract faces
                face_locations_haar = haar_cascade.detectMultiScale(
                    image, scaleFactor=1.2, minNeighbors=5, minSize=(50, 50)
                )

                face_locations_hog = detector(image, 1)

                if (
                    len(face_locations_haar) != 1
                    or len(face_locations_hog) != 1
                ):
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

    iterations = 15
    max_training_images = 5

    """
    results = [
        [
            [
                [
                    all tests of one iteration (as tuple)
                ]
            ] --> iterations
        ] --> n-training_images(1-5)
    ]
    """

    df = pd.DataFrame(
        columns=[
            "n_training_images",
            "true_name",
            "predicted_name",
            "smallest_distance",
        ]
    )

    # ---------------------------------------------

    auth = FaceAuthentication(benchmark_mode=True, lite=True)

    # ---------------------
    for n_training_images in range(max_training_images):
        print(
            f" @@@@@@@@@@@@@@ {n_training_images + 1} training images @@@@@@@@@@@@@@ "
        )

        for i in range(iterations):
            print(f" @@@@@@@@@@@@@@ Iteration {i + 1} @@@@@@@@@@@@@@ ")
            # training images
            training_images = dict()
            for key, values in master_dataset.items():
                training_images[key] = values[i : i + n_training_images + 1]
            # testing images
            testing_images = dict()
            for key, values in master_dataset.items():
                testing_images[key] = (
                    values[:i]
                    + values[
                        i
                        + n_training_images
                        + 1 : iterations
                        + n_training_images
                        + 1
                    ]
                )

            auth.delete_all_users()

            # train with all images from training dataset
            for name, images in training_images.items():
                for image in images:
                    try:
                        auth.register_face(name, image)
                    except:
                        print(f"Failed to register {name}")

            # test the classifier
            print(
                f'{"Actual" :<30} {"Predicted" :<30} {"Distance" :<10} {"Correct" :<5}'
            )
            for name, images in testing_images.items():
                for image in images:
                    match, distance, face_location = auth.match_face(
                        image, tolerance=10
                    )

                    if match is None or distance is None:
                        print(f'{name :<30} {"--" :<30} {"--":<10} {"--" :<5}')
                    else:
                        print(
                            f'{name :<30} {match :<30} {"{0:.4f}".format(distance) :<10} {"yes" if name == match else "no" :<5}'
                        )

                    # append row to dataframe
                    row = [n_training_images, name, match, distance]
                    df.loc[len(df)] = row

        print(df)

    df.to_csv("results.csv", index=False)


if __name__ == "__main__":
    main()
