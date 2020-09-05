from flask import Flask
# from flask_cors import CORS
from routes import Route

app = Flask(__name__)
routes_inst = Route(app)

# cors = CORS(app)
routes_inst.routes()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3333)