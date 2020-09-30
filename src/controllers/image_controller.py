from flask import jsonify
from utils.convert_base64 import Base64Convertion
import numpy as np
import imutils
from PIL import Image
import cv2 as cv
import io

class ImageController:
    def __init__(self, app):
        self.app = app

    def get_frame(self, encodedImage):
        decoded_string = Base64Convertion().decode_base_64(encodedImage)
        decoded = cv.imdecode(np.frombuffer(decoded_string, np.uint8), -1)
        
        return decoded

    def processingImage(self, image):
        decoded_string = Base64Convertion().decode_base_64(image)
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

        contours, hierarchy = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

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

    def retrieveBallCoordinates(self, frame):
        # define the lower and upper boundaries of the "green"
        # ball in the HSV color space
        # ball RGB color (150, 209, 119)
        greenLower = (29, 86, 6)
        greenUpper = (64, 255, 255)

        # resize the frame, blur it, and convert it to the HSV
        # color space
        frame = imutils.resize(frame, width=600)
        blurred = cv.GaussianBlur(frame, (11, 11), 0)
        hsv = cv.cvtColor(blurred, cv.COLOR_BGR2HSV)

        # construct a mask for the color "green", then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        mask = cv.inRange(hsv, greenLower, greenUpper)
        mask = cv.erode(mask, None, iterations=2)
        mask = cv.dilate(mask, None, iterations=2)

        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        cnts = cv.findContours(mask.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        center = None

        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv.contourArea)
            ((x, y), radius) = cv.minEnclosingCircle(c)
            M = cv.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        return center
