from flask import jsonify

class ImageController:
    def __init__(self):
        pass

    def processingImage(self):
        result = jsonify({
            'image': 'processing'
        })
        return result
