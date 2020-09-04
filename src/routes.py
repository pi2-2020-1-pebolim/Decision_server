
from flask import jsonify

def routes(app):
    @app.route('/')
    def main_route():
        result = jsonify({
            'test': 'test'
        })

        return result
