
import ftplib
import socket
from ftplib import FTP
from datetime import datetime

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
        #ftp.retrlines('LIST')
        files = ftp.nlst()
        # Retrieve the directory listing
        # Delete each file
        for file in files:
            try:
                ftp.delete(file)
                print(f"Deleted file: {file}")
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
host = '167.205.7.226'
port = '2121'
username = 'hylab'
password = 'hy4umlbT!1'

check_ftp_connection(host, username, password)
