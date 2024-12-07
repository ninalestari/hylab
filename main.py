import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os
import sys
from ftp_download import download_file_from_ftp
from f_recog import recognition

load_dotenv(".env")

def on_connect(client, userdata, flags, rc):
    print("Connected. Result code:", rc)
    if rc == 0:
        client.subscribe("hylab_pub_315")
    else:
        print("Connection failed. Result code:", rc)

def on_message(client, userdata, msg):
    local_file_path = download_file_from_ftp(msg.payload.decode())
    if local_file_path:
        recognition(local_file_path, msg.payload.decode())

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")

def main():
    rmq_username = os.environ.get("RMQ_USERNAME")
    rmq_password = os.environ.get("RMQ_PASSWORD")
    rmq_server = os.environ.get("RMQ_SERVER")

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

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
