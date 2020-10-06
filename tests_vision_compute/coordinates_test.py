# reference: https://www.pyimagesearch.com/2015/09/21/opencv-track-object-movement/

# import the necessary packages
from collections import deque
import numpy as np
import cv2
import imutils
import time

# define the lower and upper boundaries of the "white"
# ball in the HSV color space
# 32, 98%, 91% 
# 232, 126, 5
# sensitivity = 1
# whiteLower = np.array([0, 0, 255 - sensitivity], dtype=np.uint8)
# whiteUpper = np.array([255, sensitivity, 255], dtype=np.uint8)
whiteLower = np.array([0,0,0], dtype=np.uint8)
whiteUpper = np.array([0,0,255], dtype=np.uint8)

# initialize the list of tracked points, the frame counter,
# and the coordinate deltas
max_points_object = 10
pts = deque(maxlen = max_points_object)
counter = 0
(dX, dY) = (0, 0)
direction = ""

# read the frame
frame = cv2.imread('pebolim_teste_bola_branca.jpg', cv2.IMREAD_COLOR)

# resize the frame, blur it, and convert it to the HSV
# color space
frame = imutils.resize(frame, width=600)
blurred = cv2.GaussianBlur(frame, (11, 11), 0)
hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

# construct a mask for the color "green", then perform
# a series of dilations and erosions to remove any small
# blobs left in the mask
mask = cv2.inRange(hsv, whiteLower, whiteUpper)
mask = cv2.erode(mask, None, iterations=2)
mask = cv2.dilate(mask, None, iterations=2)

# find contours in the mask and initialize the current
# (x, y) center of the ball
cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
center = None

# only proceed if at least one contour was found
if len(cnts) > 0:
    # find the largest contour in the mask, then use
    # it to compute the minimum enclosing circle and
    # centroid
    c = max(cnts, key=cv2.contourArea)
    ((x, y), radius) = cv2.minEnclosingCircle(c)
    M = cv2.moments(c)
    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
    # only proceed if the radius meets a minimum size
    ball_minimum_size = 1
    if radius > ball_minimum_size:
        # draw the circle and centroid on the frame,
        # then update the list of tracked points
        cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
        cv2.circle(frame, center, 5, (0, 0, 255), -1)
        pts.appendleft(center)
        print(center)