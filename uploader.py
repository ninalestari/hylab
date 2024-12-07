import os
import time
import shutil
from ftplib import FTP

# FTP server credentials
FTP_HOST = "ftp-sth.pptik.id"
FTP_USER = "hylab"
FTP_PASS = "hy4umlbT!1"
FTP_PORT = 2121
FTP_DIR =  "raw_data"

# Define the directories
source_directory = "D:/labwork/download_image/"
upload_finished_directory = "D:/labwork/ftp_upload/"

# Ensure the directories exist
os.makedirs(source_directory, exist_ok=True)
os.makedirs(upload_finished_directory, exist_ok=True)

def upload_file_to_ftp(file_path):
    """
    Upload a file to the FTP server's raw_data directory.
    """
    try:
        # Connect to the FTP server
        with FTP() as ftp:
            ftp.connect(FTP_HOST, FTP_PORT)
            ftp.login(FTP_USER, FTP_PASS)
            
            # Change to the desired directory on the FTP server
            ftp.cwd(FTP_DIR)
            
            # Open the file in binary mode and upload it
            with open(file_path, 'rb') as file:
                ftp.storbinary(f"STOR {os.path.basename(file_path)}", file)
            
            print(f"Uploaded file: {file_path}")
    except Exception as e:
        print(f"Failed to upload {file_path}: {e}")

def move_file_to_uploaded(file_path):
    """
    Move the file from the upload directory to the uploaded directory.
    """
    destination_path = os.path.join(upload_finished_directory, os.path.basename(file_path))
    shutil.move(file_path, destination_path)
    print(f"Moved file to: {destination_path}")

def process_files():
    """
    Process all files in the upload directory.
    """
    files = os.listdir(source_directory)
    for file_name in files:
        file_path = os.path.join(source_directory, file_name)
        if os.path.isfile(file_path):
            upload_file_to_ftp(file_path)
            move_file_to_uploaded(file_path)
            time.sleep(0.5)  # 500ms delay before processing the next file

if __name__ == "__main__":
    process_files()
