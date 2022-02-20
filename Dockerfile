FROM debian:bullseye

RUN apt update && apt-get install curl gnupg ca-certificates zlib1g-dev libjpeg-dev git -y

RUN echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | tee /etc/apt/sources.list.d/coral-edgetpu.list

RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -

# maybe also: libgl1-mesa-glx
RUN apt-get update && apt-get install cmake python3 python3-pip python3-tflite-runtime -y

# maybe
RUN pip3 install --upgrade pip setuptools wheel

RUN pip3 install opencv-python-headless

RUN pip3 install dlib

RUN pip3 install numpy

RUN pip3 install imutils

RUN pip3 install "picamera[array]"

COPY ./FaceRecognition/MobileNetwork /