# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
rawCapture = PiRGBArray(camera)
# allow the camera to warmup
time.sleep(0.3)
# grab an image from the camera
camera.capture(rawCapture, format="bgr")
image = rawCapture.array
print(image)
