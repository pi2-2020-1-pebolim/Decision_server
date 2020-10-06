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

    def calibrate_field(self, image):
        decoded_string = Base64Convertion().decode_base_64(image)
        decoded = cv.imdecode(np.frombuffer(decoded_string, np.uint8), -1)
        # transform_image = cv.cvtColor(decoded, cv.COLOR_BGR2GRAY)

        # Take frame
        frame = decoded
        frame = imutils.resize(frame, width=600)

        # Convert BGR to HSV
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

        # define range of blue color in HSV
        green_lower = np.array([40, 90, 40], np.uint8) 
        green_upper = np.array([170, 255, 255], np.uint8) 

        # Threshold the HSV image to get only blue colors
        mask = cv.inRange(hsv, green_lower, green_upper)
        mask = cv.erode(mask, None, iterations=2)
        mask = cv.dilate(mask, None, iterations=2)

        # Bitwise-AND mask and original image
        # res = cv.bitwise_and(frame,frame, mask= mask)

        ret, thresh = cv.threshold(mask, 255, 255, 255)

        contours, hierarchy = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        bound_contours = []
        for contour in contours:
            bound_contours.append(cv.boundingRect(contour))

        sorted_contours = sorted(bound_contours, key=lambda x: x[0])

        (x, y, _, _) = sorted_contours[0]
        (x2, y2, w2, h2) = sorted_contours[-1]

        MARGIN_FRAME = 10

        return (
            x - MARGIN_FRAME, 
            y - MARGIN_FRAME, 
            x2 + w2 + MARGIN_FRAME, 
            y2 + h2 + MARGIN_FRAME
        )

    def retrieveBallCoordinates(self, frame):
        # define the lower and upper boundaries of the "white"
        # ball in the HSV color space
        # ball RGB color (0, 0, 0)
        whiteLower = np.array([0,0,0], dtype=np.uint8)
        whiteUpper = np.array([0,0,255], dtype=np.uint8)

        # resize the frame, blur it, and convert it to the HSV
        # color space
        frame = imutils.resize(frame, width = 600)
        blurred = cv.GaussianBlur(frame, (11, 11), 0)
        hsv = cv.cvtColor(blurred, cv.COLOR_BGR2HSV)

        # construct a mask for the color "green", then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        mask = cv.inRange(hsv, whiteLower, whiteUpper)
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
            # only proceed if the radius meets a minimum size
            # ball_minimum_size = 1
            # if radius > ball_minimum_size:
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius), (255, 0, 0), 2)
            cv2.circle(frame, center, 5, (255, 0, 0), -1)
        return [center, frame]


    def map_players(self, frame):
        # Convert BGR to HSV
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

         # define range of blue color in HSV
        blue_lower = np.array([60, 90, 60], np.uint8) 
        blue_upper = np.array([170, 255, 255], np.uint8) 

        # Threshold the HSV image to get only blue colors
        mask = cv.inRange(hsv, blue_lower, blue_upper)
        mask = cv.erode(mask, None, iterations=2)
        mask = cv.dilate(mask, None, iterations=2)

        ret, thresh = cv.threshold(mask, 255, 255, 255)

        contours, hierarchy= cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            (x, y, w, h) = cv.boundingRect(contour)
            cv.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        return frame


    def cut_deal_frame(self, image, ROI):
        decoded_string = Base64Convertion().decode_base_64(image)
        decoded = cv.imdecode(np.frombuffer(decoded_string, np.uint8), -1)

        # Take frame
        frame = decoded
        frame = imutils.resize(frame, width=600)
        
        (x, y, w, h) = ROI
        frame = frame[y:h, x:w]

        ball = self.retrieveBallCoordinates(frame)

        is_success, gray_image_array = cv.imencode('.jpg', ball[1])
        gray_image = Image.fromarray(gray_image_array)
        encoded_gray_image = Base64Convertion().encode_base_64(gray_image.tobytes()).decode('ascii')
        return encoded_gray_image