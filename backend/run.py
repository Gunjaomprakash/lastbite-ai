from flask import Flask
from app.routes import register_blueprints
from flask_cors import CORS
def create_app():
    app = Flask(__name__)
    CORS(app)
    register_blueprints(app)
    return app

if __name__ == '__main__':
    create_app().run(
        host='0.0.0.0', 
        port=5001, 
        debug=True,
        ssl_context=('cert.pem', 'key.pem') 
    )