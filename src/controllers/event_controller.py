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
from model.ball import Ball
from controllers.image_controller import ImageController 

class EventController:

    def __init__(self, app, socketio):
       
        self.socketio = socketio
        self.app = app

        self.image_controller = ImageController(app, socketio, self)

        self.field = None
        self.ball = Ball()

        self.count_send_decision = 0
        
    def define_action(self):
        DECISION_THRESHOLD = 6

        self.count_send_decision += 1

        if self.count_send_decision >= DECISION_THRESHOLD:
            decision = {
                "evenType": "action",
                "timestamp": int(time.time()),
                "desiredState": []
            }

            lanes_x_positions = self.field.lanes_real_x_positions

            lanes_y_interception = self.ball.regression.predict(
                np.array(lanes_x_positions).reshape(-1, 1)
            )

            for lane_index, lane_y_interception in enumerate(lanes_y_interception):     

                for player in self.field.players:
                    if player.laneID == lane_index:

                        if player.can_intercept(lane_y_interception):
                            
                            ball_diff_x = self.ball.real_position_ball[0] - lanes_x_positions[lane_index]

                            decision['desiredState'].append({
                                "laneID": lane_index,
                                "position": lane_y_interception - self.field.real_height / 2,
                                "kick": 0 < ball_diff_x < 35
                            })
                           
                            break
                        else:
                            pass       

            self.socketio.emit('action', decision)
            self.app.logger.info(decision)
            self.count_send_decision = 0

    def update_event(self, image):

        # autocalibration for testing
        if not self.image_controller.is_calibrated:
            self.image_controller.calibrate_field(
                image
            )
        
        # debug log
        self.app.logger.info(self.image_controller.ROI)

        result = self.image_controller.process_image(image)
        self.define_action()

        return result

    def register_event(self, event):
        
        if self.field is None:
            self.field = Field(
                lanes=event['fieldDefinition']['lanes'],
                dimensions=event['fieldDefinition']['dimensions'],
                resolution=event['cameraSettings']['resolution']
            )

    def get_field(self):
        return self.field
