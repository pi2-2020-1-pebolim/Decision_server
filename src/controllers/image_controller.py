from flask import jsonify
from utils.convert_base64 import Base64Convertion
import cv2 as cv
import io

class ImageController:
    def __init__(self, app):
        self.app = app

    def processingImage(self, image):
        decode_image = Base64Convertion().decode_base_64(image)
        img = cv.imread(io.BytesIO(decode_image))
        transform_image = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        encode_image = Base64Convertion().encode_base_64(transform_image)
        return encode_image

