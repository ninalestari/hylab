import PIL
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os
import pymongo
from datetime import datetime
import sys
from ftplib import FTP
import time
import face_recognition
from PIL import Image, ImageDraw, UnidentifiedImageError
import numpy as np
import logging
import pickle
from pathlib import Path


load_dotenv(".env")

def load_face_encodings(directory):
    encodings = []
    names = []
    for file in os.listdir(directory):
        if file.endswith('_encoding.pkl'):
            name = file.replace('_encoding.pkl', '')
            with open(os.path.join(directory, file), 'rb') as f:
                encoding = pickle.load(f)
            encodings.append(encoding)
            names.append(name)
    return names, encodings

def on_connect(client, userdata, flags, rc):
    print("Connected. Result code:", rc)
    if rc == 0:
        client.subscribe("hylab_pub_315")
    else:
        print("Connection failed. Result code:", rc)

def on_message(client, userdata, msg):
    report, log = DbConnection()
    local_file_path = download_file_from_ftp(msg.payload)
    if local_file_path:
        recognition(local_file_path, msg.payload.decode())

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")

def download_file_from_ftp(file_name):
    ftp_server = os.environ.get("FTP_SERVER")
    username = os.environ.get("FTP_USER")
    password = os.environ.get("FTP_PASS")

    ftp = FTP()
    ftp.connect(ftp_server, 2121)
    ftp.login(username, password)
    ftp.set_pasv(True)
    ftp.sendcmd('TYPE I')  # Switch to binary mode

    remote_file_path = f"/raw_data/{file_name.decode()}"
    local_file_path = f"D:/labwork/new_download_image/{file_name.decode()}"

    try:
        file_size = ftp.size(remote_file_path)
        if file_size > 0:
            with open(local_file_path, "wb") as local_file:
                ftp.retrbinary(f"RETR {remote_file_path}", local_file.write)
            print(f"File {file_name.decode()} downloaded successfully. Size: {file_size} bytes")
            return local_file_path
        else:
            print(f"File {file_name.decode()} download failed. Size: {file_size} bytes")
            return None
    except Exception as e:
        print(f"An error occurred while downloading the file: {e}")
        return None
    finally:
        ftp.quit()

def recognition(local_file_path, file_name):
    report, log = DbConnection()
    image_directory = "D:/labwork/face_model"
    known_face_encodings = []
    known_face_names = []

    for filename in os.listdir(image_directory):
        if filename.endswith((".jpg", ".jpeg", ".png")):
            filepath = os.path.join(image_directory, filename)
            image = face_recognition.load_image_file(filepath)
            face_encodings = face_recognition.face_encodings(image)
            if face_encodings:
                known_face_encodings.append(face_encodings[0])
                known_face_names.append(os.path.splitext(filename)[0])

    try:
        unknown_image = face_recognition.load_image_file(local_file_path)
        face_locations = face_recognition.face_locations(unknown_image)
        face_encodings = face_recognition.face_encodings(unknown_image, face_locations)

        pil_image = Image.fromarray(unknown_image)
        draw = ImageDraw.Draw(pil_image)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
                current_time = time.time()
                dt = datetime.fromtimestamp(current_time)
                fdt2 = dt.strftime("%d-%m-%Y %H:%M:%S")
                print("Face detected:", name, "time:", fdt2)
                 # Create the directory if it does not exist
                face_model_path = Path(f"D:/labwork/face_model/{name}")
                face_model_path.mkdir(parents=True, exist_ok=True)
                pil_image.save(face_model_path / f"{file_name.decode()}.jpg")
                print("New Face Model saved:", name)
                
                # Save the data to the database
                data_to_save = {
                    "name": name,
                    "time": fdt2,
                    "file_name": file_name.decode()
                }
                report.insert_one(data_to_save)
            else:
                print("No face detected")

            #draw_recognition_box
            draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))
            text_bbox = draw.textbbox((left, bottom), name)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 0, 255), outline=(0, 0, 255))
            draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))

        del draw
        pil_image.save(f"D:/labwork/identified_image/{file_name.decode()}.jpg")
        current_time = time.time()
        dt3 = datetime.fromtimestamp(current_time)
        fdt3 = dt3.strftime("%d-%m-%Y %H:%M:%S")
        print("Identified image saved:", file_name.decode(), "time", fdt3)
    
    except UnidentifiedImageError:
        print(f"Cannot identify image file {local_file_path}")

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

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    client.username_pw_set(rmq_username, rmq_password)
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
