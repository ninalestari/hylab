import cv2
import dlib
import numpy as np
from datetime import datetime

# Initialize dlib's face detector and facial landmark predictor
detector = dlib.get_frontal_face_detector()
model_path = "D:/labwork/shape_predictor_68_face_landmarks.dat"
predictor = dlib.shape_predictor(model_path)

# Start video capture from webcam
#cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture('rtmp://167.205.66.10:1935' )

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale frame
    faces = detector(gray, 0)

    for face in faces:
        # Get the landmarks/parts for the face.
        landmarks = predictor(gray, face)

        # Assuming that the eye coordinates are these landmarks indices
        left_eye = landmarks.part(36).x, landmarks.part(36).y
        right_eye = landmarks.part(45).x, landmarks.part(45).y

        # Draw circles on the eye positions
        cv2.circle(frame, left_eye, 2, (0, 255, 0), -1)
        cv2.circle(frame, right_eye, 2, (0, 255, 0), -1)
        time = datetime.now()

        # Print eye positions
        print(f"Left Eye Position: {left_eye}, time: {time}")
        print(f"Right Eye Position: {right_eye}, time: {time}")

    # Display the resulting frame
    cv2.imshow('Frame', frame)

    # Break the loop on pressing 'q'
    if cv2.waitKey(1000) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()

#coba buat bounding box di wajah dan terjemahkan arahnya ke dalam bentuk text