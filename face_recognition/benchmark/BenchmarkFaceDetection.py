import time
from statistics import mean

import cv2 as cv
import dlib
import imutils
from imutils import face_utils


def benchmark_haar(
    video_path,
    scaleFactor=1.1,
    minNeighbors=5,
    minSize=(50, 50),
    maxSize=(400, 400),
):
    haar_cascade = cv.CascadeClassifier(
        cv.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    # benchmark variables
    frames = 0
    detected_frames = 0
    false_detections = 0
    detection_times = []

    capture = cv.VideoCapture(video_path)
    capture.set(cv.CAP_PROP_POS_FRAMES, 0)

    while capture.isOpened():
        ret, frame = capture.read()
        if ret:
            frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            frames += 1

            frame = imutils.resize(frame, width=1600)

            # detect faces in image with haar classifier
            start = time.time_ns()
            face_locations = haar_cascade.detectMultiScale(
                frame,
                scaleFactor=scaleFactor,
                minNeighbors=minNeighbors,
                minSize=minSize,
                maxSize=maxSize,
            )
            end = time.time_ns()

            detection_times.append(end - start)

            if len(face_locations) == 1:
                detected_frames += 1
            elif len(face_locations) > 1:
                false_detections += 1

            # draw rectangles for faces
            face_locations = [
                (y, x + w, y + h, x) for (x, y, w, h) in face_locations
            ]
            for f1, f2, f3, f4 in face_locations:
                frame = cv.rectangle(frame, (f2, f1), (f4, f3), (255, 0, 0), 3)

            cv.imshow("Benchmark Video", frame)
            if cv.waitKey(1) and 0xFF == ord("d"):
                break
        else:
            break

    print(
        f"Detection Rate: {round(detected_frames / frames, 4)}, False Detection Rate: {round(false_detections / frames, 4)}, Average Detection Time: {mean(detection_times) / 10 ** 6} ms"
    )

    capture.release()
    cv.destroyAllWindows()


def benchmark_fhog(video_path, sample=0):
    face_detector = dlib.get_frontal_face_detector()

    # benchmark variables
    frames = 0
    detected_frames = 0
    detection_times = []
    false_detections = 0

    capture = cv.VideoCapture(video_path)
    capture.set(cv.CAP_PROP_POS_FRAMES, 0)

    while capture.isOpened():
        ret, frame = capture.read()
        if ret:
            frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            frames += 1

            frame = imutils.resize(frame, width=1000)

            start = time.time_ns()
            rects = face_detector(frame, sample)
            end = time.time_ns()

            detection_times.append(end - start)

            if len(rects) == 1:
                detected_frames += 1
            if len(rects) > 1:
                false_detections += 1

            for (i, rect) in enumerate(rects):
                (x, y, w, h) = face_utils.rect_to_bb(rect)
                cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            cv.imshow("Benchmark Video", frame)
            if cv.waitKey(1) and 0xFF == ord("d"):
                break
        else:
            break

    print(
        f"Detection Rate: {round(detected_frames / frames, 4)}, False Detection Rate: {round(false_detections / frames, 4)}, Average Detection Time: {mean(detection_times) / 10 ** 6} ms"
    )

    capture.release()
    cv.destroyAllWindows()


benchmark_haar(
    "videos/FaceDetectionBenchmark.mp4",
    scaleFactor=1.2,
    minNeighbors=5,
    minSize=(50, 50),
    maxSize=(300, 300),
)
# benchmark_fhog("videos/FaceDetectionBenchmark.mp4", sample=0)

"""
results:

haar, resolution (width=1000):

*) scaleFactor=1.1, minNeighbors=5, minSize=(50, 50)
    Detection Rate: 0.8345, False Detection Rate: 0.1029, Average Detection Time: 18.76585257301808 ms
    
*) scaleFactor=1.2, minNeighbors=5, minSize=(50, 50) <-- Pretty good!
    Detection Rate: 0.8567, False Detection Rate: 0.0236, Average Detection Time: 10.066801668984702 ms
    
*) scaleFactor=1.3, minNeighbors=5, minSize=(50, 50)
    Detection Rate: 0.8102, False Detection Rate: 0.009, Average Detection Time: 7.933581293463144 ms
    
*) scaleFactor=1.4, minNeighbors=5, minSize=(50, 50)
    Detection Rate: 0.5744, False Detection Rate: 0.057, Average Detection Time: 5.038853337969402 ms
    
*) scaleFactor=1.5, minNeighbors=5, minSize=(50, 50)
    Detection Rate: 0.6871, False Detection Rate: 0.0779, Average Detection Time: 5.261157301808066 ms
    
*) scaleFactor=2.0, minNeighbors=5, minSize=(50, 50)
    Detection Rate: 0.3282, False Detection Rate: 0.0014, Average Detection Time: 2.00048066759388 ms
    
haar, resolution (width=1600):

*) scaleFactor=1.2, minNeighbors=5, minSize=(50, 50)
    Detection Rate: 0.8102, False Detection Rate: 0.0542, Average Detection Time: 23.302725034770514 ms
    
*) scaleFactor=1.2, minNeighbors=5, minSize=(80, 80), maxSize=(400,400)
    Detection Rate: 0.8296, False Detection Rate: 0.0271, Average Detection Time: 9.324152016689846 ms
    
------------------------------------------------------------
    
fhog, resolution (width=1000)
   sample=0:
        Detection Rate: 0.6426, False Detection Rate: 0.016, Average Detection Time: 35.50722496522949 ms --> 28 fps
   sample=1:
        Detection Rate: 0.9332, False Detection Rate: 0.0146, Average Detection Time: 140.3804278859527 ms --> 7 fps
        
fhog, resolution (width=600)
   sample=0:
        Detection Rate: 0.194, False Detection Rate: 0.0, Average Detection Time: 13.710500347705146 ms
   sample=1:
        Detection Rate: 0.7378, False Detection Rate: 0.0188, Average Detection Time: 52.947139638386645 ms
        
fhog, resolution (width=800)
   sample=0:
        Detection Rate: 0.4993, False Detection Rate: 0.0035, Average Detection Time: 23.008160917941584 ms    
   sample=1:
        Detection Rate: 0.9284, False Detection Rate: 0.0202, Average Detection Time: 92.8917123783032 ms
   
fhog, resolution (width=1600)
   sample=0:
        Detection Rate: 0.9332, False Detection Rate: 0.0195, Average Detection Time: 89.3963057023644 ms
   sample=1:
        --- 
        
        
    
"""
