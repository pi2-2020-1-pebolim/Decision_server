import math
from math import dist

from numpy.core.numerictypes import find_common_type
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
from model.player import Player
from controllers.image_controller import ImageController
from controllers.machine_state_controller import MachineStateController 

class DecisionController:

    def __init__(self, app, socketio, event_controller: 'EventController' ):
       
        self.socketio = socketio
        self.app = app

        self.event_controller = event_controller
        self.ball = event_controller.ball
        self.latest_decision = None
        self.last_timestamp = None
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

    def get_timtestamp(self):

        if self.last_timestamp is None:
            self.last_timestamp = int(time.time())
        
        self.last_timestamp += 1
        return self.last_timestamp

    def build_decision(self, desired_state_list):
        return {
            "evenType": "action",
            "timestamp": self.get_timtestamp(),
            "desiredState": desired_state_list
        }

    def build_desired_state(self, lane_id, distance, kick):
        return {
            "laneID": lane_id,
            "position": distance,
            "kick": kick
        }

    def verify_inertia(self, direction):
        if direction != "no_move":
            return (None, "left_direction")
        else:

            # action to perform when no move or very low movement detected
            defense_lane, _, _, real_ball_position = self.find_defense_lane()
            
            desired_states = []
            for lane_id, players in self.field.players_in_lane.items():
                
                if lane_id == defense_lane:
                    player, dist = self.find_closest_player(players, *real_ball_position)
                    desired_states.append(self.build_desired_state(
                        lane_id,
                        player.clamp_position(dist[1]),
                        1 < dist[0] < 8
                    ))

            return (self.build_decision(desired_states), "stop")

    def find_closest_player(self, players, x, y):
        closest_player =  min(players, key=lambda p: p.distance_from_point(x, y))
        return closest_player, closest_player.split_distance_from_point(x, y)

    def find_defense_lane(self):
        
        lanes_x_positions = self.field.lanes_real_x_positions
        lanes_y_interception = self.ball.estimate_position(lanes_x_positions)

        real_ball_position = self.ball.real_position_ball

        # the closest lane to the left should follow the ball movement
        # the others behind it should be on a predicted point

        defense_lane = None
        for laneID, position in reversed(list(enumerate(lanes_x_positions))):
            defense_lane = laneID

            # if ball is ahead this is the defense lane is correct
            if real_ball_position[0] > position:
                break 
        
        return defense_lane, lanes_x_positions, lanes_y_interception, real_ball_position


    def calculate_decision(self, direction):
        if direction == "left":

            # the ball is coming towards our goal, defend it always
            
            defense_lane, lanes_x_positions, lanes_y_interception, real_ball_position = self.find_defense_lane()
            
            desired_state_for_lane = {}
            for lane_index, players in self.field.players_in_lane.items():
                if lane_index == defense_lane:
                    
                    closest_player, split_distance = self.find_closest_player(players, *real_ball_position)
                    desired_state = self.build_desired_state(
                        lane_index,
                        closest_player.clamp_position(split_distance[1]),
                        0 < split_distance[0] < 15
                    )
                    
                    desired_state_for_lane[lane_index] = desired_state

                elif lane_index < defense_lane:
                    available_players = list(filter(lambda x: x.can_intercept(lanes_y_interception[lane_index]), players))
                    
                    if len(available_players) == 0:
                        continue
                    
                    closest_player, split_distance = self.find_closest_player(
                        players,
                        lanes_x_positions[lane_index],
                        lanes_y_interception[lane_index]
                    )

                    desired_state = self.build_desired_state(
                        lane_index,
                        closest_player.clamp_position(split_distance[1]),
                        0 < split_distance[0] < 15
                    )

                    desired_state_for_lane[lane_index] = desired_state
        
            return (self.build_decision(list(desired_state_for_lane.values())), "left")
        else:
            return (None, "right_direction")

    def defense_position_technique(self, direction):

        # the ball is moving towards the enemy goal
        # get out of the way and prepare for a counter attack

        desired_state_for_lane = {}

        ball_pos = self.ball.real_position_ball
        lanes_x_positions = self.field.lanes_real_x_positions
        lanes_y_interception = self.ball.estimate_position(lanes_x_positions)

        for lane_index, interception_point in enumerate(lanes_y_interception):
            
            players = self.field.players_in_lane[lane_index]
            ball_dist_x = ball_pos[0] - lanes_x_positions[lane_index]
            
            # get out of the way
            if ball_pos[0] > lanes_x_positions[lane_index]:
                player, distance = self.find_closest_player(players, lanes_x_positions[lane_index], interception_point)
                max_player_move = player.yMaxPosition - player.yCenterPosition
                desired_distance = max_player_move / 4

                if distance[1] < desired_distance:
                    dist_to_center = distance[1] - player.yCenterPosition
                    position = player.clamp_position(dist_to_center - (desired_distance - distance[1]))

                    
                    desired_state_for_lane[lane_index] = self.build_desired_state(
                        lane_index,
                        position,
                        1 < ball_dist_x < 7
                    )

            # prepare for a counter attack
            elif ball_pos[0] < lanes_x_positions[lane_index]:

                inverse_interception_point = self.field.real_height - interception_point 

                player, distance = self.find_closest_player(
                    players,
                    lanes_x_positions[lane_index],
                    inverse_interception_point
                )

                desired_state_for_lane[lane_index] = self.build_desired_state(
                    lane_index,
                    player.clamp_position(distance[1]),
                    1 < ball_dist_x < 5
                )

        return (self.build_decision(list(desired_state_for_lane.values())), "right")
        
    def define_action(self):
        DECISION_THRESHOLD = 2

        self.count_send_decision += 1

        if self.count_send_decision >= DECISION_THRESHOLD:
            
            decision = self.machine_state.run(self.ball.direction)
            # decision =  self.build_decision([self.build_desired_state(0, 8, False)])
            # decision = self.build_decision([
            #     self.build_desired_state(
            #         lane_id,
            #         self.find_closest_player(
            #             self.field.players_in_lane[lane_id],
            #             *self.ball.real_position_ball
            #         )[0].clamp_position(
            #             self.find_closest_player(
            #                 self.field.players_in_lane[lane_id],
            #                 *self.ball.real_position_ball
            #             )[1][1]
            #         ),
            #         False
            #     ) 
            #     for lane_id in range(len(self.field.lanes_real_x_positions)) 
            # ])   
            
            if decision is not None: 
                self.socketio.emit('action', decision)
                self.latest_decision = decision
            
            self.count_send_decision = 0
