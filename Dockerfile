FROM arm32v7/python:3.9.7-buster

RUN pip install --upgrade pip setuptools wheel

ENV READTHEDOCS True

RUN pip install --no-cache-dir picamera

COPY ./FaceRecognition /

CMD ["python3", "/MobileNetwork/camera.py"]

