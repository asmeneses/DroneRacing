from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
from sqlalchemy.orm import scoped_session
from .gcs_manager import upload_to_gcs
import uuid
import json
from .pubsub_manager import publish_message

from .models import Status, User, Video
from .models import Session

api = Blueprint('api', __name__)

@api.route('/')
def index():
    return jsonify({'message': 'Welcome to the API'}), 200


@api.route('/auth/signup', methods=['POST'])
def signup():
    data = request.json

    if 'username' not in data:
        return jsonify({'message': 'Username is required'}), 400

    if 'email' not in data:
        return jsonify({'message': 'Email is required'}), 400

    if 'password1' not in data:
        return jsonify({'message': 'Password is required'}), 400

    if 'password2' not in data:
        return jsonify({'message': 'Password confirmation is required'}), 400

    username = data['username']
    email    = data['email']
    password = data['password1']
    conf_password = data['password2']

    db = scoped_session(Session)

    if db.query(User).filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 409

    if db.query(User).filter_by(username=email).first():
        return jsonify({'message': 'Email already exists'}), 409

    if password != conf_password:
        return jsonify({'message': 'Passwords do not match'}), 400

    new_user = User(username=username, email=email)
    new_user.password = password

    db.add(new_user)
    db.commit()

    return jsonify({'message': 'User created successfully'}), 201

@api.route('/auth/login', methods=['POST'])
def login():
    data = request.json

    if 'username' not in data:
        return jsonify({'message': 'Username is required'}), 400

    if 'password' not in data:
        return jsonify({'message': 'Password is required'}), 400

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
    data = request.json

    tasks = []
    db = scoped_session(Session)

    if 'max' in data:
        max = data['max']
        limit = int(max)
        if limit < 0:
            limit = 0
        tasks = db.query(Video).limit(limit).all()
    else:
        tasks = db.query(Video).all()

    try:
        order = data['order']
        sorted_tasks = []
        if order is not None:
            numOrder = int(order)
            if numOrder == 1:
                sorted_tasks = sorted(tasks, key=lambda x: x.id, reverse=True)
            else:
                sorted_tasks = sorted(tasks, key=lambda x: x.id)
        else:
            sorted_tasks = sorted(tasks, key=lambda x: x.id)

        return jsonify([t.json() for t in sorted_tasks]), 200
    except Exception as e:
        return jsonify({'message': f'{e}'}), 500

@api.route('tasks', methods=['POST'])
@jwt_required()
def create_task():
    # Check if the request contains a file
    if 'file' not in request.files:
        return 'No file part in the request', 400

    file = request.files['file']

    # Check if file is empty
    if file.filename == '':
        return 'No selected file', 400

    # Check if file is an mp4 video
    if not file.filename.endswith('.mp4'):
        return 'Uploaded file is not an MP4 video', 400

    buket_filename = str(uuid.uuid4()) + ".mp4"

    upload_to_gcs(buket_filename, file)

    video = Video(
        filename = file.filename,
        status = Status.UPLOADED,
        bucket_filename = buket_filename
    )

    db = scoped_session(Session)

    db.add(video)
    db.commit()

    message = json.dumps({"videoId": video.id, "buketFilename": buket_filename})
    project_id = "soluciones-cloud-420918"
    topic_id = "videos_queue"

    publish_message(project_id, topic_id, message)

    return jsonify({'status': 'upload started', 'video_id': video.id}), 201

@api.route('tasks/<int:id>', methods=['GET'])
@jwt_required()
def get_task(id):
    try:
        db = scoped_session(Session)
        task = db.query(Video).filter_by(id=id).first()
        if task:
            return jsonify(task.json()), 200
        return jsonify({'message': 'Task not found'}), 404
    except Exception as e:
        return jsonify({'message': f'{e}'}), 500

@api.route('tasks/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_task(id):
    try:
        db = scoped_session(Session)
        task = db.query(Video).filter_by(id=id).first()
        if task:
            db.delete(task)
            db.commit()
            return jsonify({'message': 'Task deleted successfully'}), 200
        return jsonify({'message': 'Task not found'}), 404
    except Exception as e:
        return jsonify({'message': f'{e}'}), 500