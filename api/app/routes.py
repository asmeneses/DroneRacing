from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
from celery import Celery
from sqlalchemy.orm import scoped_session
import os

from .models import Status, User, Video
from .models import Session

api = Blueprint('api', __name__)
celery = Celery('tasks' , broker=os.getenv('BROKER_URL'))

@api.route('/auth/signup', methods=['POST'])
def signup():
    data = request.json

    username = data['username']
    email    = data['email']
    password = data['password']

    db = scoped_session(Session)

    if db.query(User).filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 409

    if db.query(User).filter_by(username=email).first():
        return jsonify({'message': 'Email already exists'}), 409

    new_user = User(username=username, email=email)
    new_user.password = password

    db.add(new_user)
    db.commit()

    return jsonify({'message': 'User created successfully'}), 201

@api.route('/auth/login', methods=['POST'])
def login():
    data = request.json

    username = data['username']

    db = scoped_session(Session)

    user = db.query(User).filter_by(username=username).first()

    if user is None or user.check_password(data['password']) is False:
        return jsonify({'message': 'Invalid credentials'}), 401

    token = create_access_token(identity=user.id)
    return jsonify({'token': token}), 200

@api.route('tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    # TODO: Implement this
    return jsonify({'message': 'Task list'}), 200

@api.route('tasks', methods=['POST'])
@jwt_required()
def create_task():
    key = 'fileName'

    if key not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files[key]
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file.filename.endswith('.mp4') is False:
        return jsonify({'error': 'Invalid file format. Use .mp4 files'}), 400

    video = Video(
        filename = file.filename,
        status = Status.UPLOADING
    )

    db = scoped_session(Session)

    db.add(video)
    db.commit()

    # task = celery.send_task(name='upload_video', args=[video_path, video.id])
    # return jsonify({'status': 'upload started', 'task_id': task.id, 'video_id': video.id}), 201
    return jsonify({'message': 'Task created successfully'}), 201


@api.route('tasks/<int:id>', methods=['GET'])
@jwt_required()
def get_task(id):
    # TODO: Implement this
    return jsonify({'message': 'Task details'}), 200

@api.route('tasks/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_task(id):
    # TODO: Implement this
    return jsonify({'message': 'Task deleted successfully'}), 200