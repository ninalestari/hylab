import ftplib
from io import BytesIO
import numpy as np
import cv2
import face_recognition
from datetime import datetime
import os

FTP_HOST = "ftp-sth.pptik.id"
FTP_USER = "hylab"
FTP_PASS = "hy4umlbT!1"
FTP_PORT = 2121
FTP_FOLDER_PATH = "/raw_data"

def enhance_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    eq = cv2.equalizeHist(gray)
    enhanced_image = cv2.cvtColor(eq, cv2.COLOR_GRAY2BGR)
    return enhanced_image

def process_images(folder_path):
    with ftplib.FTP() as ftp:
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(FTP_USER, FTP_PASS)
        ftp.cwd(folder_path)
        ftp.voidcmd('TYPE I')  # Ensure we're in binary mode
        response = []
        ftp.retrlines('MLSD', response.append)

        for entry in response:
            details = dict(item.split('=', 1) for item in entry.split(';')[:-1])
            filename = entry.split(';')[-1].strip()
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                mod_time = details['modify']
                #formatted_time = f"{mod_time[:4]}-{mod_time[4:6]}-{mod_time[6:8]} {mod_time[8:10]}:{mod_time[10:12]}:{mod_time[12:14]}"
                formatted_time = f"{mod_time[:4]}-{mod_time[4:6]}-{mod_time[6:8]} {mod_time[9:11]}:{mod_time[11:13]}:{mod_time[13:15]} {mod_time[16:]}"
                #if datetime.strptime(formatted_time, "%Y-%m-%d %H:%M:%S") >= datetime.strptime("2024-08-06 09:00:00", "%Y-%m-%d %H:%M:%S"):
                if datetime.strptime(formatted_time, "%Y-%m-%d %I:%M:%S %p") >= datetime.strptime("2024-08-06 08:00:00 AM", "%Y-%m-%d %I:%M:%S %p"):
                    try:
                        img_data = BytesIO()
                        ftp.retrbinary('RETR ' + filename, img_data.write)
                        if img_data.tell() == 0:
                            raise ValueError("No data received from FTP server")
                        img_data.seek(0)
                        np_img = np.frombuffer(img_data.getvalue(), dtype=np.uint8)
                        image = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
                        enhanced_image = enhance_image(image)
                        face_locations = face_recognition.face_locations(enhanced_image)
                        if len(face_locations) > 0:
                            print(f"{filename}: Found {len(face_locations)} face(s), timestamp: {formatted_time}")
                            for (top, right, bottom, left) in face_locations:
                                cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
                            font = cv2.FONT_HERSHEY_SIMPLEX
                            cv2.putText(image, f"Timestamp: {formatted_time}", (10, 30), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
                            #cv2.imshow('Detected Faces', image)
                            #cv2.waitKey(0)
                            # Save the image to local drive
                            save_path = os.path.join('D:/labwork/img_download', filename)
                            cv2.imwrite(save_path, image)

                        else:
                            print(f"{filename}: No faces detected, timestamp: {formatted_time}")
                    except Exception as e:
                        print(f"Error processing {filename}: {e}")
        cv2.destroyAllWindows()

process_images(FTP_FOLDER_PATH)
