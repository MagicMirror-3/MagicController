import cv2

# open camera
cap = cv2.VideoCapture(0)

# set dimensions
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# take frame
ret, frame = cap.read()
print(ret, frame)
# write frame to file
cv2.imwrite('image.jpg', frame)
# release camera
cap.release()
