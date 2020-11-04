from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from routes import Route
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_pi2!'
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    max_queue=None,
    max_size=None,
    ping_timeout=5,
    ping_interval=10
)
routes_inst = Route(app, socketio)
logging.basicConfig(level=logging.DEBUG)

cors = CORS(app, resources={r"*": {"origins": "*"}})
routes_inst.routes()

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=3333)
