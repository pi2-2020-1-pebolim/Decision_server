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

class Ball:
   
    def __init__(self):
        self.DEQUE_MAX = 10
        self.deque_memory = deque(maxlen=self.DEQUE_MAX)
   
        self.regression = LinearRegression()
        self.direction = 'no_move'
   
        self.real_position_ball = None

    def update_position(self, point):

        self.deque_memory.appendleft(point)
        
        self.real_position_ball = point

        self.fit_regression()
    
    def fit_regression(self):

        if len(self.deque_memory) >= self.DEQUE_MAX:
            x_positions, y_positions = zip(*self.deque_memory)

            self.regression.fit(
                np.array(x_positions).reshape(-1, 1), np.array(y_positions)
            )

            self.direction = 'no_move'

            if x_positions[-1] < x_positions[0]:
                self.direction = 'right'
            elif x_positions[-1] > x_positions[0]:
                self.direction = 'left'

    def estimate_position(self,  x):
        return self.regression.predict(
            np.array(x).reshape(-1, 1)
        )
