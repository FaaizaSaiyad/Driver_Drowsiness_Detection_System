import cv2
import numpy as np
import dlib
from imutils import face_utils
import serial
import time

# Serial communication with Arduino
s = serial.Serial('COM3', 9600)

# Start camera
cap = cv2.VideoCapture(0)

# Load face detector and landmark predictor
hog_face_detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# State counters
sleep = 0
drowsy = 0
active = 0
status = ""
color = (0, 0, 0)

# Helper Functions
def compute(ptA, ptB):
    return np.linalg.norm(ptA - ptB)

def blinked(a, b, c, d, e, f):
    up = compute(b, d) + compute(c, e)
    down = compute(a, f)
    ratio = up / (2.0 * down)
    if ratio > 0.25:
        return 2
    elif 0.21 < ratio <= 0.25:
        return 1
    else:
        return 0

def is_yawning(landmarks):
    top_lip = landmarks[62]
    bottom_lip = landmarks[66]
    mouth_opening = compute(top_lip, bottom_lip)
    return mouth_opening > 20

# Main loop
while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = hog_face_detector(gray)

    for face in faces:
        x1, y1 = face.left(), face.top()
        x2, y2 = face.right(), face.bottom()
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        landmarks = predictor(gray, face)
        landmarks = face_utils.shape_to_np(landmarks)

        left_blink = blinked(landmarks[36], landmarks[37],
                             landmarks[38], landmarks[41],
                             landmarks[40], landmarks[39])
        right_blink = blinked(landmarks[42], landmarks[43],
                              landmarks[44], landmarks[47],
                              landmarks[46], landmarks[45])

        # Blink Detection
        if left_blink == 0 or right_blink == 0:
            sleep += 1
            drowsy = 0
            active = 0
            if sleep > 6:
                status = "SLEEPING !!!"
                color = (0, 0, 255)
                s.write(b'a')
                time.sleep(0.5)

        elif left_blink == 1 or right_blink == 1:
            sleep = 0
            active = 0
            drowsy += 1
            if drowsy > 6:
                status = "Drowsy !"
                color = (0, 0, 255)
                s.write(b'a')
                time.sleep(0.5)

        else:
            drowsy = 0
            sleep = 0
            active += 1
            if active > 6:
                status = "Active :)"
                color = (0, 255, 0)
                s.write(b'b')
                time.sleep(0.5)

        # Yawning
        if is_yawning(landmarks):
            status = "Yawning!"
            color = (0, 0, 255)
            s.write(b'a')
            time.sleep(0.5)

        # Display status
        cv2.putText(frame, status, (100, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

        for n in range(0, 68):
            (x, y) = landmarks[n]
            cv2.circle(frame, (x, y), 1, (255, 255, 255), -1)

    cv2.imshow("Frame", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
