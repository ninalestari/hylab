from ftplib import FTP, FTP_TLS, error_perm, all_errors
import socket
import logging

# Enable logging
logging.basicConfig(level=logging.DEBUG)

def connectFTP():
    ftp_server = "ftp-sth.pptik.id"
    username = "hylab"
    password = "hy4umlbT!1"
    port = 2121
    #ftp_server = "183.91.79.104"
    #username = "nina"
    #password = "Harysa1409"
    #port = 22

    try:
        ftp = FTP()
        #ftp.set_debuglevel(2)  # Enable debug output
        ftp.connect(ftp_server, port)
        print("Connected to the server")
        ftp.login(user=username, passwd=password)
        print("Logged in successfully")
        ftp.set_pasv(True)  # Enable passive mode
        print("Passive mode enabled")
        
        # List files in the root directory
        #files = ftp.nlst()
        ftp.cwd('/raw_data')  # Replace with the path to your 'raw_data' directory if necessary
        ftp.retrlines('LIST')
        files = ftp.nlst()
        print("Files in directory:", files)
        ftp.quit()
        print("Connection closed")
    except (socket.error, socket.gaierror) as e:
        print(f"Network error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

connectFTP()

