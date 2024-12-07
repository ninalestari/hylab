import face_recognition
from PIL import Image
import numpy as np
import cv2

cap = cv2.VideoCapture(0)
check = cap.isOpened()
print("Camera Stream Status: ", check)

# Load a sample picture and learn how to recognize it.
image = face_recognition.load_image_file("D:/labwork/cropped_face.jpg")
face_encodings = face_recognition.face_encodings(image)

print("Face encodings:", face_encodings)

image = face_recognition.load_image_file("D:/labwork/face_model_comvis/ninalestari.jpg")
face_locations = face_recognition.face_locations(image, model="cnn")
print ("Face locations:", format(len(face_locations)))

for face_location in face_locations:

    # Print the location of each face in this image
    top, right, bottom, left = face_location
    print("A face is located at pixel location Top: {}, Left: {}, Bottom: {}, Right: {}".format(top, left, bottom, right))

    # You can access the actual face itself like this:
    face_image = image[top:bottom, left:right]
    pil_image = Image.fromarray(face_image)
    pil_image.show()