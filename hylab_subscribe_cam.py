import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os
import sys
from datetime import datetime
from ftplib import FTP
import time
from urllib.parse import quote
from PIL import Image, ImageDraw, UnidentifiedImageError
from urllib3.util.retry import Retry

load_dotenv(".env")

def on_connect(client, userdata, flags, rc):
    print("Connected. Result code: " + str(rc))
    # Subscribe to a topic
    client.subscribe("hylab_pub_315")


def on_message(client, userdata, msg):
    ftp_server = os.environ.get("FTP_SERVER")
    username = os.environ.get("FTP_USER")
    password = os.environ.get("FTP_PASS")

    # Encode the username and password for the URL
    encoded_username = quote(username, safe='')
    encoded_password = quote(password, safe='')

    # Connect to the FTP server
    ftp = FTP(ftp_server)
    ftp.set_pasv(True)  # Enable passive mode
    ftp.connect(ftp_server, 2121)
    ftp.login(username, password)
    msg_text = str(msg.payload, encoding='utf-8', errors='ignore')
    current_time = time.time()
    dt = datetime.fromtimestamp(current_time)
    fdt = dt.strftime("%d-%m-%Y %H:%M:%S")
    print("Received message: " + msg_text, "time: ", fdt)
    file_name = msg_text
    remote_file_path = "/raw_data/{}".format(file_name)
    
    local_file_path = "D:/labwork/new_download_image/{}".format(
        file_name)
    # Download the file
    try:
        size = ftp.size(remote_file_path)
        print("Size: ", size)
        if size > 0:
            with open(local_file_path, "wb") as local_file:
                ftp.retrbinary("RETR " + remote_file_path, local_file.write)
        else:
            print("File size is too small")
    except Exception as e:
        pass

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")

def main():
    rmq_username = os.environ.get("RMQ_USERNAME")
    rmq_password = os.environ.get("RMQ_PASSWORD")
    rmq_server = os.environ.get("RMQ_SERVER")

    # Create an MQTT client instance
    client = mqtt.Client()

    # Assign callback functions
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    client.publish("hylab_pub_315", "Hello, MQTT!")
    client.username_pw_set("/{}:hylab".format(rmq_username), rmq_password)
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