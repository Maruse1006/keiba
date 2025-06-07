from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from models import db, bcrypt
from register import register_blueprint
from login import login_blueprint
from get_horse import get_horses_blueprint
from payout import check_payout_blueprint
from get_daily_profit import get_daily_profit_blueprint
from horse_pedigree_api import horse_pedigree_api_blueprint
from bet import bet_api_blueprint

app = Flask(__name__)

# CORSを有効化
CORS(app)

# Flaskアプリケーションの設定
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://flaskuser:flaskpassword@localhost/keiba'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

# ライブラリの初期化
db.init_app(app)  # models.py で定義した db を初期化
bcrypt.init_app(app)

# JWTの初期化とエラーハンドラの追加
jwt = JWTManager(app)

@jwt.unauthorized_loader
def custom_unauthorized_response(err_str):
    print(f"[JWT ERROR] Missing or invalid auth header: {err_str}")
    return jsonify({"error": "Missing or invalid Authorization header"}), 401

@jwt.invalid_token_loader
def custom_invalid_token_response(err_str):
    print(f"[JWT ERROR] Invalid token: {err_str}")
    return jsonify({"error": "Invalid token"}), 422

@jwt.expired_token_loader
def custom_expired_token_response(jwt_header, jwt_payload):
    print(f"[JWT ERROR] Token expired")
    return jsonify({"error": "Token expired"}), 401

# Blueprintの登録
app.register_blueprint(register_blueprint, url_prefix='/api')
app.register_blueprint(login_blueprint, url_prefix='/api')
app.register_blueprint(get_horses_blueprint, url_prefix='/api')
app.register_blueprint(check_payout_blueprint, url_prefix='/api')
app.register_blueprint(get_daily_profit_blueprint, url_prefix='/api')
app.register_blueprint(horse_pedigree_api_blueprint, url_prefix='/api')
app.register_blueprint(bet_api_blueprint, url_prefix='/api')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # テーブルを作成
        print("Database tables created successfully!")
    app.run(host='0.0.0.0', port=5000, debug=True)
