
from flask import jsonify, render_template, request, make_response, json
from controllers.image_controller import ImageController
from flask_socketio import emit, send
from json import loads
import time
from collections import deque

class Route:
    def __init__(self, app, socketio):
        self.app = app
        self.socketio = socketio
        self.image_inst = ImageController(self.app)
        self.image = ''
        self.calibrate = False
        self.cordinate_calibration = (0, 0, 0, 0)
        self.counter = 0
        self.execution_times = deque(maxlen = 100)

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


        @self.app.route('/calibrate', methods=['GET'])
        def calibrate_screen():
            try:
                if not self.calibrate:
                    self.app.logger.info(self.image)
                    self.calibrate = True
                    self.cordinate_calibration = self.image_inst.calibrate_field(self.image)
                    self.app.logger.info('passou')
                    self.app.logger.info(self.cordinate_calibration)
                return {}
            except:
                return {}

        @self.app.route('/api/status_update', methods=['POST'])
        def status_update():
            
            if request.method == 'POST':
                data = loads(request.data)
                self.image = data['camera']['image'] 

                if self.calibrate:
                    # center_pos = self.image_inst.retrieveBallCoordinates(self.image_inst.get_frame(data['camera']['image']))

                    # self.app.logger.info(f"Center: {center_pos[0]}, {center_pos[1]}")
                    
                    start_time = time.time()
                    self.counter += 1
        
                    field_image = self.image_inst.cut_deal_frame(self.image, self.cordinate_calibration)

                    self.execution_times.append(time.time() - start_time)

                    self.app.logger.info(f"Medições: {self.counter}")

                    if self.counter % 250 == 0:
                        file_name = f"{time.strftime('%Y%m%d_%H%M%S')}.txt"
                        file = open(file_name, 'a+')
                        for execution_time in self.execution_times:
                            file.write(f"{execution_time}\n")
                        file.close()
                    
                    self.socketio.emit('update_image', {
                        'image': f"data:image/jpeg;base64,{field_image}"
                    })

            return "OK"

    def setup_socketio(self):
        pass