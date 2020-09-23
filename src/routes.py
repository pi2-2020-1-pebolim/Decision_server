
from flask import jsonify, render_template, request, make_response, json
from controllers.image_controller import ImageController
from flask_socketio import emit, send

from json import loads

class Route:
    def __init__(self, app, socketio):
        self.app = app
        self.socketio = socketio
        self.image_inst = ImageController(self.app)
        self.image = ''

    def routes(self):

        self.setup_socketio()

        @self.app.route('/save')
        def main_route():
            return render_template('index.html', image='')

        @self.app.route('/', methods=['POST', 'GET'])
        def render_image():
            if request.method == 'POST':
                self.image = self.image_inst.processingImage(request.form['image'])
                return self.image
            else:
                result = jsonify({
                    'hello': 'world'
                })
                self.socketio.emit('update_image', result)

                return result

    def setup_socketio(self):
      
        @self.socketio.on('status_update')
        def get_image_event(json):
            
            json = loads(json)

            encoded_image = self.image_inst.processingImage(json['camera']['image'])
            self.socketio.emit('update_image', {
                'image': f"data:image/jpeg;base64,{encoded_image}"
            })
            # emit('back_resp', json)

        @self.socketio.on('test')
        def get_teste(json):
            return jsonify({
                'hello': 'world'
            })
            