FROM python:3.9-bullseye

RUN apt update && apt-get install curl gnupg ca-certificates zlib1g-dev libjpeg-dev git cmake -y

RUN echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | tee /etc/apt/sources.list.d/coral-edgetpu.list

RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -

# RUN apt-get update && apt-get install -y build-essential

# maybe
RUN pip3 install --upgrade pip setuptools wheel

RUN pip3 install --no-cache-dir tflite-runtime>=2.7.0
RUN pip3 install --no-cache-dir tflite-support>=0.3.1 dlib imutils

# RUN pip3 install cmake==3.22.0

RUN pip3 install --no-cache-dir numpy>=1.20.0
RUN pip3 install --no-cache-dir opencv-python~=4.5.3.56

#ENV READTHEDOCS True

#RUN pip3 install --no-cache-dir picamera

#COPY ./FaceRecognition /

#CMD ["python3", "/MobileNetwork/test.py"]

# get camera working
# get
