
from math import dist
from typing import Match
import math


class Player:

    def __init__(self, laneID, xPosition, yCenterPosition, movementLimit):
        super().__init__()

        self.laneID = laneID
        
        self.xPosition = xPosition
        self.yCenterPosition = yCenterPosition
        self.current_position = self.yCenterPosition

        self.yMaxPosition = 0
        self.yMinPosition = 0
        self.set_y_max_min_positions(movementLimit)

    def clamp_position(self, position):
        
        target_position = self.yCenterPosition + position

        # lower than minimum
        if target_position <= self.yMinPosition:
            # return as negative value, since the rod should move
            # downwards
            return -(self.yCenterPosition - self.yMinPosition)
        
        # grater than maximum
        if target_position >= self.yMaxPosition:
            return self.yMaxPosition - self.yCenterPosition

        return position
    
    def split_distance_from_point(self, x, y):
        return (
            x - self.xPosition,
            y - self.current_position
        )
    
    def distance_from_point(self, x, y):
        point_distance = self.split_distance_from_point(x, y)
        return math.sqrt(point_distance[0]**2 + point_distance[1]**2)

    
    def set_y_max_min_positions(self, movementLimit):
        self.yMaxPosition = self.yCenterPosition + movementLimit
        self.yMinPosition = self.yCenterPosition - movementLimit

    def can_intercept(self, real_y):
        return self.yMinPosition <= real_y <= self.yMaxPosition

    def update_position(self, distance):
        self.current_position = self.yCenterPosition + distance