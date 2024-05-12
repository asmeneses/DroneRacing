from flask import Flask
from flask_jwt_extended import JWTManager
import os

jwt = JWTManager()

def create_app():
    app = Flask(__name__)

    from .routes import worker
    app.register_blueprint(worker)

    from .models import User, Status, Video

    return app