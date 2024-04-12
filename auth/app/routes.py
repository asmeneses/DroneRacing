from flask import Blueprint, request, jsonify
from .models import User, db
from flask_jwt_extended import create_access_token

auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['POST'])
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


@auth.route('/login', methods=['POST'])
def login():
    data = request.json

    user = User.query.filter_by(username=data['username']).first()

    if user is None or user.check_password(data['password']) is False:
        return jsonify({'message': 'Invalid credentials'}), 401

    token = create_access_token(identity=user.id)
    return jsonify({'token': token}), 200