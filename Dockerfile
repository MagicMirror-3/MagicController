FROM debian:buster

RUN apt update && apt-get install curl gnupg ca-certificates zlib1g-dev libjpeg-dev git -y

RUN echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | tee /etc/apt/sources.list.d/coral-edgetpu.list

RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -

RUN apt-get update && apt-get install python3 python3-pip -y

RUN pip3 install https://github.com/google-coral/pycoral/releases/download/release-frogfish/tflite_runtime-2.5.0-cp37-cp37m-linux_armv7l.whl

RUN git clone -b PyDeploy https://github.com/n1klasD/MagicController.git

RUN cd /MagicController

RUN git checkout PyDeploy

RUN pip3 install -r requirements.txt

# execute script
WORKDIR /MagicController/FaceRecognition/MobileNetwork
CMD ["python3","FaceAuthentication.py"]