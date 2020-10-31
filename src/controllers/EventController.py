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


class EventController:

    def __init__(self, app, socketio):
       
        self.socketio = socketio
        self.app = app

        self.image_controller = None

        self.field = None
        self.ball = None
        


    def update_event(self, image, ROI):
        
        self.image_controller
        self.define_action()

        frame = self._debug_frame(frame)

        return encode_string_from_frame(frame)

    def register_event(self, event):
        
        self.field = Field(
            lanes=event['fieldDefinition']['lanes'],
            dimensions=event['fieldDefinition']['dimensions'],
            resolution=event['cameraSettings']['resolution']
        )

    def get_field(self):
        return self.field
