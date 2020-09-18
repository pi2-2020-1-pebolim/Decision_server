import base64

class Base64Convertion:

    def __init__(self):
        pass

    def decode_base_64(self, image):
        return base64.b64decode(image)
        

    def encode_base_64(self, image):
        return base64.b64encode(image)