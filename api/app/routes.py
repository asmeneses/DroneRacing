from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
from .models import User, db

api = Blueprint('api', __name__)

@api.route('/auth/signup', methods=['POST'])
def signup():
    data = request.json

    username = data['username']
    email    = data['email']
    password = data['password']

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already exists'}), 409

    new_user = User(username=username, email=email)
    new_user.password = password

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201


@api.route('/auth/login', methods=['POST'])
def login():
    data = request.json

    user = User.query.filter_by(username=data['username']).first()

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
    # TODO: Implement this
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