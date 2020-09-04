from flask import Flask
from flask_cors import CORS
from routes import routes

app = Flask(__name__)
cors = CORS(app)
routes(app)

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=3333)