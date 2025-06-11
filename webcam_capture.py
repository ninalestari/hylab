import cv2
import time
from datetime import datetime
import os
from ftplib import FTP
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

# Konfigurasi FTP
FTP_HOST = os.getenv("FTP_HOST")
FTP_PORT = int(os.getenv("FTP_PORT", 21))
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")
FTP_FOLDER = os.getenv("FTP_ENGAGEMENT", "/")

# Konfigurasi MongoDB
mongo_client = MongoClient("mongodb://engagement:ZWlbWVudA5nYWd!@103.150.60.151:27017/engagement")
db = mongo_client["engagement"]
collection = db["raw_image"]

# Folder lokal
local_folder = "C:/Users/Acer`/PROJECT/hylab/worker-face-detection-service/captured_images"
os.makedirs(local_folder, exist_ok=True)

def upload_to_ftp(local_file, remote_file):
    with FTP(FTP_HOST) as ftp:
        ftp.login(FTP_USER, FTP_PASS)
        ftp.cwd(FTP_FOLDER)
        with open(local_file, 'rb') as f:
            ftp.storbinary(f'STOR {remote_file}', f)
    print(f"🌐 File {remote_file} di-upload ke FTP.")

def save_to_db(filename, timestamp, user_id):
    data = {
        "filename": filename,
        "timestamp": timestamp,
        "user_id": user_id
    }
    collection.insert_one(data)
    print(f"🗃️ Data disimpan ke MongoDB: {data}")

def start_capture(user_id):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Tidak bisa membuka webcam.")
        return

    print(f"📸 Capture dimulai untuk user_id: {user_id}. Tekan Ctrl+C untuk berhenti.")
    try:
        while True:
            ret, frame = cap.read()
            if ret:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{user_id}_{timestamp}.jpg"
                local_path = os.path.join(local_folder, filename)

                cv2.imwrite(local_path, frame)
                upload_to_ftp(local_path, filename)
                save_to_db(filename, timestamp, user_id)

            time.sleep(15)

    except KeyboardInterrupt:
        print("\n🛑 Capture dihentikan.")
    cap.release()
    cv2.destroyAllWindows()

# === Main ===
if __name__ == '__main__':
    user_input = input("Masukkan '1' untuk mulai, lalu masukkan ID user: ").strip()
    if user_input == "1":
        user_id = input("Masukkan ID user: ").strip()
        start_capture(user_id)
    else:
        print("⏹️ Dibatalkan.")
