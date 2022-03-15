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

RUN pip install --no-cache-dir falcon requests

# install nodejs and magicMirror
RUN curl -sL https://deb.nodesource.com/setup_16.x | bash
RUN apt install -y nodejs
RUN git clone https://github.com/MichMich/MagicMirror
WORKDIR /MagicMirror
RUN npm install --only=prod --omit=dev

# install magicModule
WORKDIR /MagicMirror/modules
RUN git clone https://github.com/n1klasD/MagicModule

WORKDIR /

# install MagicController
RUN mkdir MagicController
COPY . /MagicController
WORKDIR /MagicController
#RUN pip3 install -r requirements_raspberry.txt

RUN chmod a+x entrypoint.sh
WORKDIR /

CMD ["MagicController/entrypoint.sh"]

# start magicMirrorpi
# start start Controller

