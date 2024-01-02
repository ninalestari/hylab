import mysql.connector
import requests
import os

# Database connection parameters change to yours
host=host,
database=database,
user=user,
password=password

# Establishing the connection
conn = mysql.connector.connect(
    host=host,
    database=database,
    user=user,
    password=password
)
print (f"Connection established: {conn.is_connected()}")

# Creating a cursor object to interact with the database
cursor = conn.cursor()
query = "SELECT faceimage FROM mdl_proctoring_face_images WHERE facefound = '1';"  # Replace with your actual query
cursor.execute(query)

def get_filename():
    filename = image_url.split('/')[-1]
    #print(f"Downloading image {filename}...")
    return filename

# Downloading and saving images
for (image_url,) in cursor: 
    #print(f"Image URL: {image_url}")
    if image_url:
    # Making a request to the image URL
        response = requests.get(image_url)
        #print(f"Status code: {response.status_code}")
        if response.status_code == 200:
        # Extracting image filename from URL
            filename = get_filename()
            #filename = image_url.split('/')[-1]
            #filepath = os.path.join(image_dir, filename)
            #print(f"Downloading image {filename}...")
            parts = filename.split('-')
            if (len(parts) >2):
                desired_number = parts[2]
                #print(f"id: {desired_number}")
                image_dir = f"D:/labwork/proc_image/new_images/{desired_number}/"
                if not os.path.exists(image_dir):
                    os.makedirs(image_dir)
                filepath = os.path.join(image_dir, filename)
                print (f"image saved to: {filepath}")

            # Saving the image
            with open(filepath, 'wb') as file:
                file.write(response.content)
                #print(f"Image saved to {filepath}")
            
count_documents = cursor.rowcount
print(f"Number of documents downloaded: {count_documents}")


# Closing the connection
cursor.close()
conn.close()
