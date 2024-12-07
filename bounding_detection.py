'''
from PIL import Image

# Load the image
img = Image.open("D:/labwork/download_image/RrbSVZJgD9A-FUtNufe4W.jpg")

# Get image dimensions
width, height = img.size

print(f'Width: {width}, Height: {height}')

# Adding a border to the image
border_color = 'black'  # Color of the border
border_width = 10  # Width of the border in pixels

# Create a new image with border
new_img = Image.new('RGB', (width + 2*border_width, height + 2*border_width), border_color)
new_img.paste(img, (border_width, border_width))

# Save or display the new image
new_img.save('D:/labwork/kit_detection/RrbSVZJgD9A-FUtNufe4W.jpg')
new_img.show()
'''

import cv2
import numpy as np

# Load the image
image = cv2.imread('D:/labwork/download_image/RrbSVZJgD9A-FUtNufe4W.jpg')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
cv2.imshow('Original', gray)
# Apply edge detection
edged = cv2.Canny(gray, 30, 200)

# Find contours
contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Function to check if a contour is a rectangle
def is_rectangle(contour):
    # Approximate the contour to a polygon
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
    # The contour is a rectangle if it has 4 vertices
    return len(approx) == 4

# Loop over the contours
for contour in contours:
    if is_rectangle(contour):
        # Draw the rectangle on the image
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

# Show the result
cv2.imshow('Detected Rectangles', image)
cv2.waitKey(0)
cv2.destroyAllWindows()

