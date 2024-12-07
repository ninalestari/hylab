
import PIL
import os
import pymongo
from datetime import datetime
import wget
import sys
from ftplib import FTP
import pytz 
import time
from urllib.parse import quote
import face_recognition
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
import uuid
import pickle

cap = cv2.VideoCapture('rtmp://167.205.66.10:1935' )

#cap = cv2.VideoCapture(0)
check = cap.isOpened()
print ("Camera Stream Status: ", check)

while True:
    ret, frame = cap.read()
    resize = cv2.resize(frame, (640,480))
    cv2.imshow('Video', resize)
                       
    #process_this_frame = not process_this_frame  
    
      # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
cap.release()
cv2.destroyAllWindows()
