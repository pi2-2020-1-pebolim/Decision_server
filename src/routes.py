
from flask import jsonify, render_template, request
from controllers.image_controller import ImageController
from flask_socketio import emit


class Route:
    def __init__(self, app, socketio):
        self.app = app
        self.socketio = socketio
        self.image_inst = ImageController()
        self.image = ''

    def routes(self):
        @self.app.route('/save')
        def main_route():
            return render_template('index.html', image=self.image)

        @self.app.route('/', methods=['POST', 'GET'])
        def render_image():
            if request.method == 'POST':
                self.image = self.image_inst.processingImage(request.form['image'])
                return self.image
            else:
                result = jsonify({
                    'hello': 'world'
                })

                return result

        @self.socketio.on('image_transfer')
        def get_image_event(json):
            emit('update_image', json)

        @self.socketio.on('test', namespace='/test')
        def get_teste(json):
            emit('update_image', jsonify({
                'test': 'test'
            }))
