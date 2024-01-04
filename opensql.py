import mysql.connector
import requests
import os
from datetime import datetime
import pymongo
import pytz
import wget
from ftplib import FTP
import ftplib

load_dotenv(".env")

def new_connection():
    return mysql.connector.connect(
        host=os.environ.get("MDL_FTP"),
        database="os.environ.get("MDL_DB")",
        user="os.environ.get("MDL_ADMIN")",
        password=os.environ.get("MDL_PASS")"
    )

def DbConnection():
    db = os.environ.get("MONGODB")
    myclient = pymongo.MongoClient(db)
    db = myclient["engagement"]
    collection_log = db["log"]
    collection_report = db["proctoring"]
    return collection_report, collection_log

report,log = DbConnection()

def ftp_connect(filename, filepath):
    try:
        ftp_server = "ftp5.pptik.id"
        username = "engagement"
        password = "dAZWlbWVu5nYWd!"

        # Connect to the FTP server
        ftp = FTP(ftp_server)
        ftp.set_pasv(True)  # Enable passive mode
        ftp.connect(ftp_server, 2121)
        ftp.login(username, password)
        
        #ftp.cwd('/proctoring')
        directory = f'/proctoring/{format(get_username(filename))}'

        # Try to change to the directory. If it fails, create it.
        try:
            ftp.cwd(directory)
        except ftplib.error_perm:
            # If the directory doesn't exist, create it and then change to it.
            ftp.mkd(directory)
            ftp.cwd(directory)
        
        # Upload the file
        remote_file_path = directory + '/' + filename

        with open(filepath, 'rb') as file:
            ftp.storbinary(f'STOR {os.path.basename(remote_file_path)}', file)
        # Close the FTP connection
        ftp.quit()

        print(f"File uploaded successfully to {remote_file_path}")
    except Exception as e:
        print(f"FTP error: {e}")

def new_buffered_cursor(conn):
    return conn.cursor(buffered=True)

def get_filename(image_url):
    return image_url.split('/')[-1]

def get_username(filename):
    parts = filename.split('-')
    if len(parts) > 2:
        return parts[2]
    return "unknown"

def get_coursename(filename):
    parts = filename.split('-')
    if len(parts) > 3:
        id_course = parts[3]
    return id_course

def get_timestamp(filename):
    parts = filename.split('-')[4]
    time_parts = parts.split('.')
    if len(parts) > 1:
        time = time_parts[0]
        timestamp_ms = int(time)
        timestamp_s = timestamp_ms/1000 
        date_time = datetime.utcfromtimestamp(timestamp_s)
        fmt_datetime = date_time.strftime('%Y-%m-%d %H:%M:%S')
        #print(date_time)  # Outputs the date and time in UTC        
    return fmt_datetime

def save_to_path(image_url, response, username, filename,):
    image_dir = f"D:/labwork/proc_image/new_images/{username}/"
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    filepath = os.path.join(image_dir, filename)
    with open(filepath, 'wb') as file:
        file.write(response.content)
    #print(f"Image saved to: {filepath}")
    return filepath

def main(conn):
    cursor = new_buffered_cursor(conn)
    query = "SELECT faceimage FROM mdl_proctoring_face_images WHERE facefound = '1';"
    cursor.execute(query)
    
    for (image_url,) in cursor:
        if image_url:
            response = requests.get(image_url)
            if response.status_code == 200:
                #get function
                filename = get_filename(image_url)
                username = get_username(filename)
                coursename = get_coursename(filename)
                timestamp = get_timestamp(filename)
                path= save_to_path(image_url, response, username, filename)
                ftp_connect(filename, path)
                remove_local = os.remove(path)
                print(f"File removed: {remove_local}")
                # Close and reopen the connection for a new query
                conn.close()
                conn = new_connection()
                new_cursor = new_buffered_cursor(conn)
                query_id = "SELECT username FROM mdl_user WHERE id = %s"
                id_user = (username,)  # Ensure it's a tuple
                new_cursor.execute(query_id, id_user)
                xresult = new_cursor.fetchone()
                for x in xresult:
                    print(f"username: {x}")
                
                # Close and reopen the connection for a new query
                conn.close()
                conn = new_connection()
                new_cursor = new_buffered_cursor(conn)
                coursename = get_coursename(filename)
                #print(f"coursename for id {coursename} is: {coursename}")
                query_course = "SELECT fullname FROM mdl_course WHERE id = %s"
                id_course = (coursename,)  # Ensure it's a tuple
                new_cursor.execute(query_course, id_course)
                yresult = new_cursor.fetchone()
                for y in yresult:
                    print(f"coursename: {y}")
                # Close and reopen the connection for a new query
                print (f"timestamp: {timestamp}")

                # Save to MongoDB
                data_to_save = {
                    "image_url": image_url,
                    "username": x,
                    "course": y,
                    "timestamp": timestamp,
                    "expression": "-"
                }
                # Insert into the MongoDB collection
                report.insert_one(data_to_save)

    cursor.close()

if __name__ == "__main__":
    conn = new_connection()
    print(f"Connection established: {conn.is_connected()}")
    #get_coursename(filename)
    main(conn)
    conn.close()
