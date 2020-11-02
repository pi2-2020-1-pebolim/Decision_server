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
from controllers.machine_state_controller import MachineStateController 

class DecisionController:

    def __init__(self, app, socketio, event_controller: 'EventController' ):
       
        self.socketio = socketio
        self.app = app

        self.event_controller = event_controller
        self.ball = event_controller.ball
        # self.field is a property function

        self.count_send_decision = 0
        self.machine_state = MachineStateController()

        self.machine_state.add_state("stable", self.verify_inertia)
        self.machine_state.add_state("left_direction", self.calculate_decision)
        self.machine_state.add_state("right_direction", self.defense_position_technique)

        states = ["stop", "left", "right"]

        for state in states:
            self.machine_state.add_state(state, None, end_state=1)

        self.machine_state.set_start("stable")

    @property
    def field(self) -> Field:
        return self.event_controller.get_field()

    def verify_inertia(self, direction):
        if direction is not "stable":
            return (None, "left_direction")
        else:
            return (None, "stop")

    def calculate_decision(self, direction):
        if direction is "left":

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

            return (decision, "left")
        else:
            return (None, "right_direction")

    def defense_position_technique(self, direction):
        decision = {
            "evenType": "action",
            "timestamp": int(time.time()),
            "desiredState": []
        }

        desired_state_for_lane = {}

        for i in range(4):
            desired_state = {
                "laneID": i,
                "position": 0,
                "kick": False
            }

            desired_state_for_lane[i] = desired_state

        decision['desiredState'] = list(desired_state_for_lane.values())

        return (decision, "right")
        
    def define_action(self):
        DECISION_THRESHOLD = 3

        self.count_send_decision += 1

        if self.count_send_decision >= DECISION_THRESHOLD:
            
            decision = decision = self.machine_state.run(self.ball.direction)
            
            if decision is not None: 
                self.socketio.emit('action', decision)
                self.app.logger.info(decision)
            
            self.count_send_decision = 0
