
from flask import jsonify, render_template, request
from controllers.image_controller import ImageController


class Route:
    def __init__(self, app):
        self.app = app
        self.image_inst = ImageController()

    def routes(self):
        @self.app.route('/save')
        def main_route():
            return render_template('index.html')

        @self.app.route('/', methods=['POST', 'GET'])
        def render_image():
            if request.method == 'POST':
                return self.image_inst.processingImage()
            else:
                result = jsonify({
                    'hello': 'world'
                })

                return result
