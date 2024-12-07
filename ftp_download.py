import os
from ftplib import FTP

def download_file_from_ftp(file_name):
    ftp_server = os.environ.get("FTP_SERVER")
    username = os.environ.get("FTP_USER")
    password = os.environ.get("FTP_PASS")

    ftp = FTP()
    ftp.connect(ftp_server, 2121)
    ftp.login(username, password)
    ftp.set_pasv(True)
    ftp.sendcmd('TYPE I')  # Switch to binary mode

    remote_file_path = f"/raw_data/{file_name}"
    local_file_path = f"D:/labwork/new_download_image/{file_name}"

    try:
        file_size = ftp.size(remote_file_path)
        if file_size > 0:
            with open(local_file_path, "wb") as local_file:
                ftp.retrbinary(f"RETR {remote_file_path}", local_file.write)
            print(f"File {file_name} downloaded successfully. Size: {file_size} bytes")
            return local_file_path
        else:
            print(f"File {file_name} download failed. Size: {file_size} bytes")
            return None
    except Exception as e:
        print(f"An error occurred while downloading the file: {e}")
        return None
    finally:
        ftp.quit()
