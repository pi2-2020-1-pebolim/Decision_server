from utils.convert_base64 import Base64Convertion
from sklearn.linear_model import LinearRegression
from collections import deque
from flask import jsonify
from PIL import Image

import numpy as np
import imutils
import cv2 as cv
import io
import time

from model.field import Field


class ImageController:
    def __init__(self, app, socketio):
        self.DEQUE_MAX = 10
        self.deque_memory = deque(maxlen=self.DEQUE_MAX)
        self.socketio = socketio
        self.app = app
        self.regression = LinearRegression()
        self.position_x_rods = []
        self.direction = 'no_move'
        self.position_ball = None
        self.count_send_decision = 0
        self.rods_info = []
        self.half_field_size = 0
        self.field = Field()
        self.MARGIN_FRAME = 25

    def register_event(self, event):
        self.field.set_field_dimensions(event['fieldDefinition']['dimensions'])
        self.field.set_image_dimensions(event['cameraSettings']['resolution'])
        self.field.scale_real_dimensions_field()
        self.field.set_lanes_players_positions(
            event['fieldDefinition']['lanes']
        )

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
        # frame = imutils.resize(frame, width=600)

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

        contours, hierarchy = cv.findContours(
            mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE
        )

        bound_contours = []
        for contour in contours:
            bound_contours.append(cv.boundingRect(contour))

        sorted_contours = sorted(bound_contours, key=lambda x: x[0])

        (x, y, _, _) = sorted_contours[0]
        (x2, y2, w2, h2) = sorted_contours[-1]

        MARGIN_FRAME = 0

        # self.map_rods_cpu_position(frame)
        self.app.logger.info(self.position_x_rods)

        x_position = x - MARGIN_FRAME
        y_position = y - MARGIN_FRAME
        width = x2 + w2 + MARGIN_FRAME
        height = y2 + h2 + MARGIN_FRAME

        return (x_position, y_position, width, height)

    def retrieve_ball_coordinates(self, frame):
        # define the lower and upper boundaries of the "white"
        # ball in the HSV color space
        # ball RGB color (0, 0, 0)
        white_lower = np.array([150, 10, 50], dtype=np.uint8)
        white_upper = np.array([255, 255, 255], dtype=np.uint8)

        # resize the frame, blur it, and convert it to the HSV
        # color space
        # frame = imutils.resize(frame, width = 600)
        blurred = cv.GaussianBlur(frame, (11, 11), 0)
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

        # construct a mask for the color "green", then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        mask = cv.inRange(hsv, white_lower, white_upper)
        mask = cv.erode(mask, None, iterations=2)
        mask = cv.dilate(mask, None, iterations=2)

        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        contours = cv.findContours(
            mask.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE
        )
        contours = imutils.grab_contours(contours)
        center = None

        # only proceed if at least one contour was found
        if len(contours) > 0:
            # find the largest contour in the mask, then usse
            # it to compute the minimum enclosing circle and
            # centroid
            max_contour = max(contours, key=cv.contourArea)
            ((x, y), radius) = cv.minEnclosingCircle(max_contour)
            M = cv.moments(max_contour)
            center = (
                int(M["m10"] / M["m00"]), 
                int(M["m01"] / M["m00"])
            )
            self.position_ball = center
            self.deque_memory.appendleft(center)

            # only proceed if the radius meets a minimum size
            # ball_minimum_size = 1
            # if radius > ball_minimum_size:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv.circle(frame, (int(x), int(y)), int(radius), (255, 0, 0), 2)
        return [center, frame]

    def verify_next_positions(self, list_positions):
        new_list_positions = list_positions.copy()
        for position in range(len(list_positions)):
            if position != 0:
                if list_positions[position] - list_positions[position - 1] < 5:
                    new_list_positions.remove(list_positions[position])

        return new_list_positions

    def map_rods_cpu_position(self, frame):
        # Convert BGR to HSV
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

        # define range of blue color in HSV
        blue_lower = np.array([70, 150, 150], np.uint8)
        blue_upper = np.array([140, 255, 255], np.uint8)

        # Threshold the HSV image to get only blue colors
        mask = cv.inRange(hsv, blue_lower, blue_upper)
        mask = cv.erode(mask, None, iterations=2)
        mask = cv.dilate(mask, None, iterations=2)

        ret, thresh = cv.threshold(mask, 255, 255, 255)

        contours, hierarchy = cv.findContours(
            mask,
            cv.RETR_EXTERNAL,
            cv.CHAIN_APPROX_SIMPLE
        )

        self.position_x_rods = []
        for contour in contours:
            (x, y, w, h) = cv.boundingRect(contour)
            cv.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            self.position_x_rods.append(x + (w // 2))

        self.position_x_rods = list(set(self.position_x_rods))
        self.position_x_rods.sort()

        self.position_x_rods = self.verify_next_positions(self.position_x_rods)
        self.app.logger.info(self.position_x_rods)

    def estimate_positions(self, frame):

        if len(self.deque_memory) >= self.DEQUE_MAX:
            x_positions, y_positions = zip(*self.deque_memory)

            self.regression.fit(
                np.array(x_positions).reshape(-1, 1), np.array(y_positions)
            )

            starting_point = [x_positions[0], y_positions[0]]
            last_queue_point = [x_positions[-1], y_positions[-1]]
            end_point = [0, 0]
            
            self.direction = 'no_move'

            diff = end_point[0] - starting_point[0]
            prediction = self.regression.predict(
                np.array(last_queue_point[0] + diff).reshape(-1, 1)
            )
            end_point[0] = prediction

            if x_positions[-1] < x_positions[0]:
                self.direction = 'right'
            elif x_positions[-1] > x_positions[0]:
                self.direction = 'left'

            end_point[1] = self.regression.coef_[
                0] * end_point[0] + self.regression.intercept_

            COLOR_LINE = (0, 50, 255)
            THICKNESS = 3

            frame = cv.line(
                frame,
                (tuple(list(map(lambda x: int(x), starting_point)))),
                (tuple(list(map(lambda x: int(x), end_point)))),
                COLOR_LINE,
                THICKNESS
            )

            return frame

    def define_action(self):
        DECISION_THRESHOLD = 6

        self.count_send_decision += 1

        if self.count_send_decision >= DECISION_THRESHOLD:
            decision = {
                "evenType": "action",
                "timestamp": int(time.time()),
                "desiredState": []
            }

            lanes_x_positions = self.field.lanes_x_positions

            lanes_y_interception = self.regression.predict(
                np.array(lanes_x_positions).reshape(-1, 1)
            )

            

            for lane_index, lane_y_interception in enumerate(lanes_y_interception):     

                for player in self.field.players:
                    if player.laneID == lane_index:
                        y_max_position = player.get_y_max_positions()
                        y_min_position = player.get_y_min_positions()
                        if lane_y_interception >= y_min_position and lane_y_interception <= y_max_position:
                            
                            ball_diff = self.position_ball[0] - lanes_x_positions[lane_index]

                            decision['desiredState'].append({
                                "laneID": lane_index,
                                "position": lane_y_interception - self.field.real_height / 2,
                                "kick": 0 < ball_diff < 35
                            })
                           
                            break
                        else:
                            pass

       

            self.socketio.emit('action', decision)
            self.app.logger.info(decision)
            self.count_send_decision = 0

    def cut_deal_frame(self, image, ROI):
        decoded_string = Base64Convertion().decode_base_64(image)
        decoded = cv.imdecode(np.frombuffer(decoded_string, np.uint8), -1)

        # Take frame
        frame = decoded
        # frame = imutils.resize(frame, width=600)

        (x, y, w, h) = ROI
        frame = frame[y:h, x:w]

        ball = self.retrieve_ball_coordinates(frame)
        frame = self.estimate_positions(ball[1])

        COLOR_LINE = (0, 50, 255)
        THICKNESS = 3

        for i in self.position_x_rods:
            frame = cv.line(
                frame,
                (int(i), int(0)),
                (int(i), int(300)),
                COLOR_LINE,
                THICKNESS
            )

        # self.map_rods_cpu_position(frame)

        font = cv.FONT_HERSHEY_SIMPLEX
        corner = (50,50)
        fontScale = 1
        fontColor = (255,255,255)
        lineType = 2

        cv.putText(
            frame,
            f'X:{int(self.position_ball[0])}, Y: {int(self.position_ball[1])}', 
            corner, 
            font, 
            fontScale,
            fontColor,
            lineType
        )


        is_success, gray_image_array = cv.imencode('.jpg', frame)
        gray_image = Image.fromarray(gray_image_array)
        encoded_gray_image = Base64Convertion().encode_base_64(
            gray_image.tobytes()
        ).decode('ascii')

        self.define_action()

        return encoded_gray_image
