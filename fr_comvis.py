import PIL
import os
import pymongo
from datetime import datetime
import wget
import sys
from ftplib import FTP
import pytz 
import time
from urllib.parse import quote
import face_recognition
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
import uuid
import pickle

cap = cv2.VideoCapture(0)
#cap = cv2.VideoCapture(1)
check = cap.isOpened()
print("Camera Stream Status: ", check)

directory = "D:/labwork/face_model_comvis"
# Arrays to hold face encodings and names
known_face_encodings = []
known_face_names = []
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

# Load encoding data
def load_face_encodings(directory):
    encodings = []
    names = []
    # Loop through each file in the directory
    for file in os.listdir(directory):
        if file.endswith('_encoding.pkl'):
            # Extract the person's name from the filename
            name = file.replace('_encoding.pkl', '')
            # Load the face encoding from the file
            with open(os.path.join(directory, file), 'rb') as f:
                encoding = pickle.load(f)
            encodings.append(encoding)
            names.append(name)
    return names, encodings

while True:
    ret, frame = cap.read()
    cv2.imshow('Video', frame)
    
    if process_this_frame:
        known_face_names, known_face_encodings = load_face_encodings(directory)
        small_frame = cv2.resize(frame, None, fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(small_frame)
        face_encodings = face_recognition.face_encodings(small_frame, face_locations)
        #print(face_encodings)
        delay = 1
        time.sleep(delay)
        #print("delaying for", delay, "seconds")
        print("faces found: ", len(face_locations))
        pil_image = Image.fromarray(rgb_small_frame)
        # Create a Pillow ImageDraw Draw instance to draw with
        draw = ImageDraw.Draw(pil_image)

        # Loop through each face found in the unknown image
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            #print("face_distances:", face_distances)

            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                else:
                    print("No face detected")
            else:
                print("No known faces to compare.")

            # Draw a box around the face using the Pillow module
            draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))
            new_guid = uuid.uuid4()  # Generates a random UUID.
            #print(new_guid)
            current_time = time.time()
            dt3 = datetime.fromtimestamp(current_time)
            fdt3 = dt3.strftime("%d-%m-%Y %H:%M:%S")
            caption = name 
            # Draw a label with a name below the face
            font = ImageFont.load_default()
            text_width = draw.textlength(caption)
            draw.text((left + 6, bottom - 5),
                      caption, fill=(255, 255, 255))
            pil_image.show()
            print("Identified image saved:", name, "time", fdt3)
        # Remove the drawing library from memory as per the Pillow docs
        del draw
    
     # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)

        # You can also save a copy of the new image to disk if you want by uncommenting this line
        # pil_image.save(
        #     "D:/PROJECT/presensi/identified/{}-{}.jpg".format(name,new_guid))
        # print("Identified image saved:", name, "time", fdt3)

    process_this_frame = not process_this_frame
    
    #cv2.imshow('Video', rgb_small_frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
cap.release()
cv2.destroyAllWindows()
