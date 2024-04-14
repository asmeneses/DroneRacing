from flask import Flask
from flask_jwt_extended import JWTManager
import os

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

    jwt.init_app(app)

    from .routes import api
    app.register_blueprint(api, url_prefix='/api')

    return app