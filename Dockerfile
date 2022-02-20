FROM debian:buster

RUN apt update && apt-get install curl gnupg ca-certificates zlib1g-dev libjpeg-dev git -y

RUN echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | tee /etc/apt/sources.list.d/coral-edgetpu.list

RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -

# maybe also: libgl1-mesa-glx
RUN apt-get update && apt-get install cmake python3 python3-pip -y

# maybe
RUN pip3 install --upgrade pip setuptools wheel

RUN pip3 install https://github.com/google-coral/pycoral/releases/download/release-frogfish/tflite_runtime-2.5.0-cp37-cp37m-linux_armv7l.whl

RUN pip3 install opencv-python

RUN pip3 install dlib

RUN pip3 install numpy

RUN pip3 install imutils

COPY ./FaceRecognition/MobileNetwork /