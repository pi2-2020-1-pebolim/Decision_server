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

class DecisionController:

    def __init__(self, app, socketio, event_controller: 'EventController' ):
       
        self.socketio = socketio
        self.app = app

        self.event_controller = event_controller
        self.ball = event_controller.ball
        # self.field is a property function

        self.count_send_decision = 0

    @property
    def field(self) -> Field:
        return self.event_controller.get_field()

    def generate_decision(self):

        decision = {
            "evenType": "action",
            "timestamp": int(time.time()),
            "desiredState": []
        }

        lanes_x_positions = self.field.lanes_real_x_positions

        lanes_y_interception = self.ball.regression.predict(
            np.array(lanes_x_positions).reshape(-1, 1)
        )

        desired_state_for_lane = {}

        for player in self.field.players:
            if player.can_intercept(lanes_y_interception[player.laneID]):
                
                ball_diff_x = self.ball.real_position_ball[0] - lanes_x_positions[player.laneID]

                desired_state = {
                    "laneID": player.laneID,
                    "position": (lanes_y_interception[player.laneID] - self.field.real_height / 2) * -1,
                    "kick": 0 < ball_diff_x < 35
                }
                desired_state_for_lane[player.laneID] = desired_state
     
        decision['desiredState'] = list(desired_state_for_lane.values())

        return decision  

        
    def define_action(self):
        DECISION_THRESHOLD = 6

        self.count_send_decision += 1

        if self.count_send_decision >= DECISION_THRESHOLD:
            
            decision = self.generate_decision()

            self.socketio.emit('action', decision)
            self.app.logger.info(decision)
            self.count_send_decision = 0
