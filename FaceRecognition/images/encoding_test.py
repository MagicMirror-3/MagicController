import cv2
import base64

path = 'niklas3.jpg'
img = cv2.imread(path)
jpg_img = cv2.imencode('.jpg', img)
b64_string = base64.b64encode(jpg_img[1]).decode('utf-8')

with open(path + ".txt", "w") as file:
    file.write(b64_string)
