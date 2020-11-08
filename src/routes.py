import os
from flask import jsonify, render_template, request, make_response, json, send_from_directory
from controllers.image_controller import ImageController
from controllers.event_controller import EventController
from flask_socketio import emit, send, join_room, leave_room

import time
from collections import deque

from json import loads

class Route:
    def __init__(self, app, socketio):
        self.app = app
        self.socketio = socketio
        self.event_controller = EventController(app, socketio)
        self.image = ''
        self.counter = 0
        self.execution_times = deque(maxlen = 100)

    def routes(self):
        @self.app.route('/favicon.ico')
        def favicon():
            return send_from_directory(os.path.join(self.app.root_path, 'static/img'),
                                    'favicon.ico', mimetype='image/vnd.microsoft.icon')

        @self.app.route('/')
        def main_route():
            return render_template('start-menu.html', image='')

        @self.app.route('/calibration')
        def calibration():
            return render_template('calibration.html')

        @self.app.route('/difficulty')
        def difficulty():
            return render_template('difficulty.html')

        @self.app.route('/time')
        def time():
            return render_template('time.html')

        @self.app.route('/start')
        def start_game():
            return render_template('start_game.html')

        @self.app.route('/calibrate', methods=['GET'])
        def calibrate_screen():
            try:
                if not self.event_controller.image_controller.is_calibrated:

                    # self.app.logger.info(self.image)
                    image_controller = self.event_controller.image_controller
                    
                    image_controller.calibrate_field(
                        self.image
                    )
                    
                    # self.app.logger.info(image_controller.calibrate_field.ROI)
                    
                return {}
            except:
                return {}

        @self.app.route('/api/status_update', methods=['POST'])
        def status_update():
            
            start_time = time.time()
            self.counter += 1

            if request.method == 'POST':
                data = loads(request.data)
                # self.app.logger.info(data["lanes"])
                self.image = data['camera']['image']
                field_image = self.event_controller.update_event(data)
                
                if field_image is not None:
                    self.socketio.emit(
                        'update_image',
                        {
                            'image': f"data:image/jpeg;base64,{field_image}"
                        },
                        room='web'
                    )

            self.execution_times.append(time.time() - start_time)
            self.app.logger.info(f"Medições: {self.counter}")
            if self.counter % 250 == 0:
                file_name = f"{time.strftime('%Y%m%d_%H%M%S')}.txt"
                file = open(file_name, 'a+')
                for execution_time in self.execution_times:
                    file.write(f"{execution_time}\n")
                file.close()
    
            return "OK"

        @self.socketio.on('join')
        def on_join(data):
            username = data['username']
            room = data['room']
            join_room(room)
            send(username + ' has entered the room.', room=room)

        @self.app.route('/api/register', methods=['POST'])
        def register_event():
            data = loads(request.data)
            self.event_controller.register_event(data)

            return "OK"
