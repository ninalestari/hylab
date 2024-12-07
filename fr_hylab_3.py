import PIL
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
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
from PIL import Image, ImageDraw, UnidentifiedImageError
import numpy as np
import cv2
import logging
import uuid
import pickle

load_dotenv(".env")

# Define callback functions for connection, message received, and connection closed
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


def on_connect(client, userdata, flags, rc):
    print("Connected. Result code: " + str(rc))
    # Subscribe to a topic
    client.subscribe("hylab_pub_315")


def on_message(client, userdata, msg):
    report, log = DbConnection()
    
    ftp_server = os.environ.get("FTP_SERVER")
    username = os.environ.get("FTP_USER")
    password = os.environ.get("FTP_PASS")

    # Connect to the FTP server
    ftp = FTP()
    ftp.connect(ftp_server, 2121)
    ftp.login(username, password)
    #print("Logged in successfully")
    ftp.set_pasv(True)  # Enable passive mode
    #print("Passive mode enabled")

    msg_text = str(msg.payload, encoding='utf-8', errors='ignore')
    current_time = time.time()
    dt = datetime.fromtimestamp(current_time)
    fdt = dt.strftime("%d-%m-%Y %H:%M:%S")
    print("Received message: " + msg_text, "time: ", fdt)

    file_name = msg_text
    remote_file_path = "/raw_data/{}".format(file_name)
    local_file_path = "D:/labwork/new_download_image/{}".format(file_name)

    # Switch to binary mode before checking the file size
    ftp.sendcmd('TYPE I')

    # Check the size of the remote file
    file_size = ftp.size(remote_file_path)
        
    if file_size > 0:
        # Download the file if its size is greater than 0 KB
        with open(local_file_path, "wb") as local_file:
            ftp.retrbinary("RETR " + remote_file_path, local_file.write)
        #print(f"File {file_name} downloaded successfully. Size: {file_size} bytes")
    else:
        print(f"File {file_name} download failed. Size: {file_size} bytes")
        return
   
    # Load a sample picture from folder
    image_directory = "D:/labwork/face_model"
    # Arrays to hold face encodings and names
    known_face_encodings = []
    known_face_names = []
    
    # Loop through each file in the image directory
    for filename in os.listdir(image_directory):
        if filename.endswith((".jpg", ".jpeg", ".png")):  # Check for image files
            # Full path to the image
            filepath = os.path.join(image_directory, filename)
            # Load the image
            image = face_recognition.load_image_file(filepath)
            # Attempt to encode the face
            face_encodings = face_recognition.face_encodings(image)
            
            if face_encodings:
                # If a face is found, append the encoding and name
                known_face_encodings.append(face_encodings[0])
                # Assuming the person's name is the filename without the extension
                known_face_names.append(os.path.splitext(filename)[0])

    # Load an image with an unknown face
    try:
        unknown_image = face_recognition.load_image_file(local_file_path)

        # Find all the faces and face encodings in the unknown image
        face_locations = face_recognition.face_locations(unknown_image)
        face_encodings = face_recognition.face_encodings(unknown_image, face_locations)

        pil_image = Image.fromarray(unknown_image)
        # Create a Pillow ImageDraw Draw instance to draw with
        draw = ImageDraw.Draw(pil_image)

        # Loop through each face found in the unknown image
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
                current_time = time.time()
                dt = datetime.fromtimestamp(current_time)
                fdt2 = dt.strftime("%d-%m-%Y %H:%M:%S")
                print("Face detected:", name, "time:", fdt2)
                pil_image.save("D:/labwork/face_model/{}/{}.jpg".format(name, file_name))
                print("New Face Model saved:", name)

                # Save to MongoDB
                data_to_save = {
                    "name": name,
                    "time": fdt2,
                    "file_name": file_name
                }
                # Insert into the MongoDB collection
                report.insert_one(data_to_save)
            else:
                print("No face detected")
            # Draw a box around the face using the Pillow module
            draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))

            # Draw a label with a name below the face
            text_bbox = draw.textbbox((left, bottom), name)  # Get the bounding box of the text
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 0, 255), outline=(0, 0, 255))
            draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))

        # Remove the drawing library from memory as per the Pillow docs
        del draw

        # You can also save a copy of the new image to disk if you want by uncommenting this line
        pil_image.save("D:/labwork/identified_image/{}.jpg".format(file_name))
        current_time = time.time()
        dt3 = datetime.fromtimestamp(current_time)
        fdt3 = dt3.strftime("%d-%m-%Y %H:%M:%S")
        print("Identified image saved:", file_name, "time", fdt3)
    
    except UnidentifiedImageError:
        print(f"Cannot identify image file {local_file_path}")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")

def connectFTP():
    ftp_server = "ftp-sth.pptik.id"
    username = "hylab"
    password = os.environ.get("FTP_PASS")

    # Connect to the FTP server
    ftp = FTP(ftp_server)
    ftp.set_pasv(True)  # Enable passive mode
    ftp.connect(ftp_server, 2121)
    ftp.login(username, password)

    # Close the FTP connection
    ftp.quit()

def DbConnection():
    db = os.environ.get("MONGODB")
    myclient = pymongo.MongoClient(db)
    db = myclient["hylab"]
    collection_log = db["log"]
    collection_report = db["datahasils"]
    return collection_report, collection_log

def main():
    rmq_username = os.environ.get("RMQ_USERNAME")
    rmq_password = os.environ.get("RMQ_PASSWORD")
    rmq_server = os.environ.get("RMQ_SERVER")

    # Create an MQTT client instance
    client = mqtt.Client()

    # Assign callback functions
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    client.publish("hylab_pub_315", "Hello, MQTT!")
    client.username_pw_set("/{}:hylab".format(rmq_username), rmq_password)
    client.connect(rmq_server, 1883, 60)
    client.loop_forever()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
