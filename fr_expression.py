import face_recognition
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import matplotlib.pyplot as plt

# This is an example of running face recognition on a single image
# and drawing a box around each person that was identified.

# Load a sample picture and learn how to recognize it.
nina_image = face_recognition.load_image_file(
    "C:/Users/ASUS/Pictures/Camera Roll/WIN_20230529_15_42_53_Pro.jpg")
nina_face_encoding = face_recognition.face_encodings(nina_image)[0]
print("dataset_face_endoding: \n", nina_face_encoding, "\n")

# Load a second sample picture and learn how to recognize it.
azizah_image = face_recognition.load_image_file(
    "D:/00. Advance Computing Lab/02. SEM 2/Work/face_model/Azizah Zakiah/WhatsApp Image 2023-05-23 at 15.41.40 (1).jpeg")
azizah_face_encoding = face_recognition.face_encodings(azizah_image)[0]
# print(biden_face_encoding)

# Load a second sample picture and learn how to recognize it.
hartuti_image = face_recognition.load_image_file(
    "D:/00. Advance Computing Lab/02. SEM 2/Work/image_model/hartuti_.jpg")
hartuti_face_encoding = face_recognition.face_encodings(hartuti_image)[0]
# print(hartuti_face_encoding)

# Create arrays of known face encodings and their names
known_face_encodings = [
    nina_face_encoding,
    azizah_face_encoding,
    hartuti_face_encoding
]
known_face_names = [
    "Nina",
    "Azizah",
    "hartuti"
]

# Load an image with an unknown face
#unknown_image = face_recognition.load_image_file("D:/01. Personal/MEDIA/FOTO/Camera/1638941119913.jpg")
unknown_image = face_recognition.load_image_file(
    "D:/labwork/proc_image/webcam-75-235-22-1676346555311.png")

# Find all the faces and face encodings in the unknown image
face_locations = face_recognition.face_locations(unknown_image)
face_encodings = face_recognition.face_encodings(unknown_image, face_locations)

# print(face_encodings)

# Convert the image to a PIL-format image so that we can draw on top of it with the Pillow library
# See http://pillow.readthedocs.io/ for more about PIL/Pillow
pil_image = Image.fromarray(unknown_image)
# Create a Pillow ImageDraw Draw instance to draw with
draw = ImageDraw.Draw(pil_image)

# Loop through each face found in the unknown image
for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
    # See if the face is a match for the known face(s)
    matches = face_recognition.compare_faces(
        known_face_encodings, face_encoding)

    name = "Unknown"

    # If a match was found in known_face_encodings, just use the first one.
    # if True in matches:
    #     first_match_index = matches.index(True)
    #     name = known_face_names[first_match_index]

    # Or instead, use the known face with the smallest distance to the new face
    face_distances = face_recognition.face_distance(
        known_face_encodings, face_encoding)
    best_match_index = np.argmin(face_distances)
    if matches[best_match_index]:
        name = known_face_names[best_match_index]

    # Draw a box around the face using the Pillow module
    draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))

    # Draw a label with a name below the face
    #text_width, text_height = draw.textsize(name)
    #draw.rectangle(((left, bottom - text_height - 10),(right, bottom)), fill=(0, 0, 255), outline=(0, 0, 255))
    #draw.text((left + 6, bottom - text_height - 5),name, fill=(255, 255, 255, 255))
    print("face_location: \n", face_locations, "\n")

    print(f"face_encoding: \n",  face_encoding, "\n")

    print("face_distance: \n", face_distances, "\n")
    # accuracy = face_recognition.
    print("match_index:\n", best_match_index, "\n")
    print("Face detected:",{name}, "\n")


# Remove the drawing library from memory as per the Pillow docs
del draw

# Display the resulting image
pil_image.show()

# You can also save a copy of the new image to disk if you want by uncommenting this line
pil_image.save("image_with_boxes.jpg")
