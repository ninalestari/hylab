import cv2
import dlib
import imutils
from imutils import face_utils

# Initialize dlib's face detector (HOG-based) and then create the facial landmark predictor
model_path = "D:/labwork/shape_predictor_68_face_landmarks.dat"
predictor = dlib.shape_predictor(model_path)

detector = dlib.get_frontal_face_detector()
#predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")  # Make sure to download this model

# Load the input image and resize it
image = cv2.imread("C:/Users/ASUS/Pictures/Camera Roll/WIN_20230529_15_42_53_Pro.jpg")  # Replace 'your_image.jpg' with your image file
image = imutils.resize(image, width=500)

# Convert the image to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Detect faces in the grayscale image
rects = detector(gray, 1)

# Loop over the face detections
for (i, rect) in enumerate(rects):
    # Determine the facial landmarks for the face region
    shape = predictor(gray, rect)
    shape = face_utils.shape_to_np(shape)

    # Loop over each of the (x, y)-coordinates for the facial landmarks
    # and draw a circle over each
    for (x, y) in shape:
        cv2.circle(image, (x, y), 1, (0, 255, 0), -1)

# Show the output image with the face detections + facial landmarks
cv2.imshow("Output", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
