FROM 1646552/bullseye_opencv_tflite:0.1

ENV READTHEDOCS True

RUN pip3 install --no-cache-dir picamera

COPY ./FaceRecognition /

CMD ["python3", "/MobileNetwork/camera.py"]

