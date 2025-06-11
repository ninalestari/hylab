import os
import cv2
import face_recognition
from ultralytics import YOLO
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

# Load YOLO model
model = YOLO('yolov8n.pt')

# Load environment variables
load_dotenv(dotenv_path="C:/Users/Acer`/PROJECT/hylab/worker-face-detection-service/.env")  # pastikan sesuai lokasi file .env
MONGO_URI = os.getenv("DATABASE")
#print("[DEBUG] Isi DATABASE:", os.getenv("DATABASE"))  # Harus bukan None
#print("[ℹ️] Mencoba konek ke:", MONGO_URI)

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.server_info()
    print("[✅] Koneksi MongoDB berhasil")
except Exception as e:
    print(f"[❌] Gagal koneksi ke MongoDB: {e}")
    exit()


# Konfigurasi Database dan Collection
db = client["hylab"]
collection_recognized = db["recognized_faces"]
collection_summary = db["detection_summary"]

# Folder paths
image_folder = "C:/Users/Acer`/Downloads/downloaded_image/"
#image_folder = "C:/Users/Acer`/Downloads/downloaded_images/"
known_folder = "C:/Users/Acer`/Downloads/known_image/"
output_folder = "C:/Users/Acer`/Downloads/processed_images/"
os.makedirs(output_folder, exist_ok=True)

# Load known face encodings
known_encodings = []
known_infos = []

for filename in os.listdir(known_folder):
    if filename.lower().endswith((".jpg", ".png")):
        path = os.path.join(known_folder, filename)
        id_student = filename.split("_")[0]
        student_name = filename.split("_", 1)[1].replace("_", " ").split(".")[0]
        try:
            image = face_recognition.load_image_file(path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_encodings.append(encodings[0])
                known_infos.append({"id": id_student, "name": student_name})
        except Exception as e:
            print(f"[⚠️] Gagal load known face {filename}: {e}")

# Process each image
for img_file in os.listdir(image_folder):
    if not img_file.lower().endswith((".jpg", ".png")):
        continue

    img_path = os.path.join(image_folder, img_file)

    try:
        results = model(img_path)
    except Exception as e:
        print(f"[❌] Gagal proses YOLO pada {img_file}: {e}")
        continue

    img = cv2.imread(img_path)
    if img is None:
        print(f"[⚠️] Gambar tidak dapat dibaca: {img_path}")
        continue

    person_count = 0
    face_match_count = 0
    matched_ids = []

    # ========= Loop Deteksi YOLO dan Face Recognition =========
    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])

        if cls_id == 0:  # person
            person_count += 1
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(img, f'Person {conf:.2f}', (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            person_roi = img[y1:y2, x1:x2]
            rgb_person = cv2.cvtColor(person_roi, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_person)
            face_encodings = face_recognition.face_encodings(rgb_person, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(known_encodings, face_encoding)
                display_name = "Unknown"
                student_id = None

                if True in matches:
                    match_index = matches.index(True)
                    matched_info = known_infos[match_index]
                    student_id = matched_info["id"]
                    display_name = matched_info["name"]
                    face_match_count += 1
                    matched_ids.append(student_id)

                # Gambar kotak wajah dan nama di gambar utama
                top_abs = top + y1
                bottom_abs = bottom + y1
                left_abs = left + x1
                right_abs = right + x1

                cv2.rectangle(img, (left_abs, top_abs), (right_abs, bottom_abs), (0, 255, 0), 2)
                cv2.putText(img, display_name, (left_abs, top_abs - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

     
    # Ambil timestamp dari file (bukan waktu sekarang)
    try:
        timestamp = datetime.fromtimestamp(os.path.getmtime(img_path))
    except:
        timestamp = datetime.now()

    # Simpan ke MongoDB: recognized_faces
    for student_id in matched_ids:
        collection_recognized.insert_one({
            "id_student": student_id,
            "name":display_name,
            "image_name": img_file,
            "timestamp": timestamp
        })


    # Simpan ke MongoDB: detection_summary
    collection_summary.insert_one({
        "image_name": img_file,
        "person_count": person_count,
        "face_match_count": face_match_count,
        "timestamp": timestamp
    })

    # Simpan hasil anotasi ke folder output
    output_path = os.path.join(output_folder, img_file)
    # Setelah semua perulangan selesai

    # Tambah background hitam agar teks terbaca
    cv2.rectangle(img, (5, 5), (320, 70), (0, 0, 0), -1)

    # Tampilkan jumlah deteksi
    cv2.putText(img, f"Total Persons: {person_count}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    cv2.putText(img, f"Recognized Faces: {face_match_count}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 200), 2)
    cv2.imwrite(output_path, img)

    print(f"[✅] {img_file} | Orang: {person_count}, Wajah dikenali: {face_match_count}")
