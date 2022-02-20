FROM python:3.8-slim-bullseye

RUN apt update && apt-get install curl gnupg ca-certificates zlib1g-dev libjpeg-dev git -y

RUN echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | tee /etc/apt/sources.list.d/coral-edgetpu.list

RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -

RUN apt-get update && apt-get install -y python3-tflite-runtime

# maybe
RUN pip3 install --upgrade pip setuptools wheel

RUN pip3 install opencv-python-headless

RUN pip3 install dlib

RUN pip3 install numpy

RUN pip3 install imutils

RUN pip3 install "picamera[array]"

COPY ./FaceRecognition/MobileNetwork /


# !!! --no-cache-dir

# no cmake
# requirements just from pip:
#numpy>=1.20.0
#opencv-python~=4.5.3.56
#tflite-runtime>=2.7.0
#tflite-support>=0.3.1