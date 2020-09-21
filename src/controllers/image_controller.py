from flask import jsonify
from utils.convert_base64 import Base64Convertion
import numpy as np
from PIL import Image
import cv2 as cv
import io

class ImageController:
    def __init__(self, app):
        self.app = app

    def processingImage(self, image):
        image_string = image.split(',')[1]
        decoded_string = Base64Convertion().decode_base_64(image_string)
        decoded = cv.imdecode(np.frombuffer(decoded_string, np.uint8), -1)
        # transform_image = cv.cvtColor(decoded, cv.COLOR_BGR2GRAY)

        # Take frame
        frame = decoded
        # Convert BGR to HSV
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        # define range of blue color in HSV
        low_green = np.array([28, 43, 21])
        high_green = np.array([102, 255, 255])
        # Threshold the HSV image to get only blue colors
        mask = cv.inRange(hsv, low_green, high_green)
        mask = cv.erode(mask, None, iterations=2)
        mask = cv.dilate(mask, None, iterations=2)
        # Bitwise-AND mask and original image
        res = cv.bitwise_and(frame,frame, mask= mask)

        ret, thresh = cv.threshold(mask, 255, 255, 255)

        contours, hierarchy= cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        sorted_contours= sorted(contours, key=cv.contourArea, reverse= True)

        # the two least areas countours in hsv conversion 
        (x, y, w, h) = cv.boundingRect(sorted_contours[-1])
        (x2,y2,w2,h2) = cv.boundingRect(sorted_contours[-2])

        if x < x2:
            cv.rectangle(frame, (x - 20, y - 20), (x2 + w2 + 20, y2 + h2 + 20), (255,223,94), 10)
        else:
            cv.rectangle(frame, (x2 - 20,y2 -20), (x + w + 20, y + h + 20), (255,223,94), 10)

        is_success, gray_image_array = cv.imencode('.jpg', frame)
        gray_image = Image.fromarray(gray_image_array)
        encoded_gray_image = Base64Convertion().encode_base_64(gray_image.tobytes()).decode('ascii')
        return encoded_gray_image

