
import ftplib
import socket
from ftplib import FTP
from datetime import datetime
from dotenv import load_dotenv

def check_ftp_connection(host, username, password):
    try:
        # Test DNS resolution
        print(f"Resolving hostname: {host}")
        ip_address = socket.gethostbyname(host)
        print(f"Resolved IP address: {ip_address}")

        ftp = FTP(host)
        ftp.set_pasv(True)  # Enable passive mode
        ftp.connect(host, 2121)
        ftp.login(username, password)
        # Print the welcome message
        print(ftp.getwelcome())
        # List files in the root directory
        ftp.cwd('/raw_data')  # Replace with the path to your 'raw_data' directory if necessary
        ftp.retrlines('LIST')
        files = ftp.nlst()
        # Delete each file in the /raw_data directory
        # Delete files from August 2023
        for file in files:
            try:
                # Get the modification time of the file
                mod_time = ftp.sendcmd(f"MDTM {file}")[4:].strip()
                mod_datetime = datetime.strptime(mod_time, "%Y%m%d%H%M%S")

                # Check if the modification time is within the year 2023
                if mod_datetime.year == 2023:
                    ftp.delete(file)
                    print(f"Deleted file: {file} (Modified: {mod_datetime})")
            except Exception as e:
                print(f"Error deleting file {file}: {e}")

        #Close the connection
        ftp.quit()
        print("FTP connection successful.")
    except ftplib.all_errors as e:
        print(f"FTP connection failed: {e}")
    except socket.gaierror as e:
        print(f"Address-related error connecting to server: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Replace with your FTP server details
host = 'ftp-sth.pptik.id'
username = 'hylab'
password = 'hy4umlbT!1'

check_ftp_connection(host, username, password)
