FROM arm32v7/python:3.9.7-buster

RUN apt update && apt-get install curl gnupg ca-certificates zlib1g-dev libjpeg-dev git cmake -y

RUN echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | tee /etc/apt/sources.list.d/coral-edgetpu.list

RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -

RUN pip3 install --upgrade pip setuptools wheel

RUN pip3 install --no-cache-dir tflite-runtime>=2.7.0
RUN pip3 install --no-cache-dir tflite-support>=0.3.1 dlib imutils

RUN pip3 install --no-cache-dir numpy>=1.20.0
RUN pip3 install --no-cache-dir opencv-python~=4.5.3.56

ENV READTHEDOCS True

RUN pip install --no-cache-dir "picamera[array]"

# install nodejs and magicMirror
RUN curl -sL https://deb.nodesource.com/setup_16.x | sudo -E bash -
RUN apt install -y nodejs
RUN git clone https://github.com/MichMich/MagicMirror
RUN cd MagicMirror
RUN npm install --only=prod --omit=dev

# install magicModule
RUN cd modules
RUN git clone https://github.com/n1klasD/MagicModule

RUN cd /

# install MagicController
RUN git clone https://github.com/n1klasD/MagicController
RUN cd MagicController
RUN pip3 install -r requirements.txt

# start magicMirror
# start start Controller

