from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from routes import Route

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_pi2!'
socketio = SocketIO(app, cors_allowed_origins="*")
routes_inst = Route(app, socketio)

cors = CORS(app)
routes_inst.routes()

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=3333)