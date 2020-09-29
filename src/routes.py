
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

        @self.app.route('/')
        def main_route():
            return render_template('start-menu.html', image='')

        @self.app.route('/calibration')
        def calibration():
            return render_template('calibration.html')

        @self.app.route('/start')
        def start_game():
            return render_template('start_game.html')

        @self.app.route('/api/status_update', methods=['POST', ])
        def status_update():
            
            if request.method == 'POST':
                
                data = loads(request.data)
                encoded_image = self.image_inst.processingImage(data['camera']['image'])
                center_pos = self.image_inst.retrieveBallCoordinates(self.image_inst.get_frame(data['camera']['image']))

                self.app.logger.info(f"Center: {center_pos[0]}, {center_pos[1]}")

                self.socketio.emit('update_image', {
                    'image': f"data:image/jpeg;base64,{encoded_image}"
                })

            return "OK"

    def setup_socketio(self):
        pass