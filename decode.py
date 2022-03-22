import cv2 as cv
from util import get_image_from_base64

with open("images.txt", "r") as f:
    base64_string = f.read()

base64_string = base64_string[1:-1]
image = get_image_from_base64(base64_string)
cv.imshow("geerge", image)
cv.waitKey(0)
