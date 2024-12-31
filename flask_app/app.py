from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS  # CORSをインポート
from models import db, bcrypt
from register import register_blueprint
from login import login_blueprint

app = Flask(__name__)

# CORSを有効化（全てのオリジンを許可）
CORS(app)  # この行がCORSの設定

# Flaskアプリケーションの設定
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://flaskuser:flaskpassword@localhost/keiba'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

# ライブラリの初期化
db.init_app(app)
bcrypt.init_app(app)
JWTManager(app)

# Blueprintの登録
app.register_blueprint(register_blueprint, url_prefix='/api')
app.register_blueprint(login_blueprint, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)
