from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models import db, User, bcrypt

login_blueprint = Blueprint('login', __name__)

@login_blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    print(f"User ID: {data}, Email: {user.email}")

    # 必要なフィールドがあるか確認
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Email and password are required.'}), 400

    # データベースでユーザーを検索
    user = User.query.filter_by(email=data['email']).first()
    if not user or not bcrypt.check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Invalid email or password.'}), 401
    print(f"User ID: {user.id}, Email: {user.email}")

    # ユーザーIDとメールをトークンに含める
    token = create_access_token(identity={'id': user.id, 'email': user.email})

    return jsonify({'message': 'Login successful!', 'token': token}), 200
