from flask import jsonify
from utils.convert_base64 import Base64Convertion
import numpy as np
from PIL import Image
import cv2 as cv
import io

class ImageController:
    def __init__(self, app):
        self.app = app

    def processingImage(self, image):
        image_string = image.split(',')[1]
        decoded_string = Base64Convertion().decode_base_64(image_string)
        decoded = cv.imdecode(np.frombuffer(decoded_string, np.uint8), -1)
        transform_image = cv.cvtColor(decoded, cv.COLOR_BGR2GRAY)
        is_success, gray_image_array = cv.imencode('.jpg', transform_image)
        gray_image = Image.fromarray(gray_image_array)
        encoded_gray_image = Base64Convertion().encode_base_64(gray_image.tobytes()).decode('ascii')
        return encoded_gray_image

