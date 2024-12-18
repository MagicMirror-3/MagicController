FROM 1646552/opencv-python-pi4:latest

RUN apt-get update && apt-get install curl gnupg ca-certificates git gcc -y

# install tflite
RUN echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | tee /etc/apt/sources.list.d/coral-edgetpu.list
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
RUN pip3 install --upgrade pip setuptools wheel
RUN pip3 install --no-cache-dir tflite-runtime>=2.7.0
# RUN pip3 install --no-cache-dir tflite-support>=0.3.1

# install pycamera
ENV READTHEDOCS True
RUN pip install --no-cache-dir "picamera[array]"

RUN apt-get install cmake build-essential -y

# install python dependencies
RUN pip install --no-cache-dir wheel dlib
RUN pip install --no-cache-dir falcon requests imutils loguru

# install nodejs and magicMirror
RUN curl -sL https://deb.nodesource.com/setup_16.x | bash
RUN apt install -y nodejs
RUN git clone https://github.com/MichMich/MagicMirror
WORKDIR /MagicMirror
RUN npm install --only=prod --omit=dev

# install magicModule
WORKDIR /MagicMirror/modules
RUN git clone https://github.com/MagicMirror-3/MagicModule

# install third party modules
RUN git clone https://github.com/lavolp3/MMM-AVStock
WORKDIR /MagicMirror/modules/MMM-AVStock
RUN npm install --only=prod --omit=dev

# install MagicController
WORKDIR /
RUN mkdir MagicController
# COPY . /MagicController

COPY setup/entrypoint.sh /
# WORKDIR /MagicController/setup
RUN chmod a+x entrypoint.sh

# execute starting script
ENTRYPOINT ["/entrypoint.sh"]


