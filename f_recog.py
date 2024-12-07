import os
import time
import face_recognition
from PIL import Image, ImageDraw, UnidentifiedImageError
import numpy as np
from pathlib import Path
from datetime import datetime
from moodle_login import login_to_moodle
from utils import DbConnection

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

                face_model_path = Path(f"D:/labwork/face_model/{name}")
                face_model_path.mkdir(parents=True, exist_ok=True)

                pil_image.save(face_model_path / f"{file_name}.jpg")
                print("New Face Model saved:", name)

                data_to_save = {
                    "name": name,
                    "time": fdt2,
                    "file_name": file_name
                }
                report.insert_one(data_to_save)

                login_to_moodle(name)
            else:
                print("No face detected")

            draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))
            text_bbox = draw.textbbox((left, bottom), name)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 0, 255), outline=(0, 0, 255))
            draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))

        del draw
        identified_image_path = Path(f"D:/labwork/identified_image/{file_name}.jpg")
        identified_image_path.parent.mkdir(parents=True, exist_ok=True)
        pil_image.save(identified_image_path)
        current_time = time.time()
        dt3 = datetime.fromtimestamp(current_time)
        fdt3 = dt3.strftime("%d-%m-%Y %H:%M:%S")
        print("Identified image saved:", file_name, "time", fdt3)

    except UnidentifiedImageError:
        print(f"Cannot identify image file {local_file_path}")
