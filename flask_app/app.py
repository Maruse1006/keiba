from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from models import db, bcrypt  # models.py からインポート
from register import register_blueprint
from login import login_blueprint
from get_horse import get_horses_blueprint
from payout import check_payout_blueprint

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
JWTManager(app)

# Blueprintの登録
app.register_blueprint(register_blueprint, url_prefix='/api')
app.register_blueprint(login_blueprint, url_prefix='/api')
app.register_blueprint(get_horses_blueprint, url_prefix='/api')
app.register_blueprint(check_payout_blueprint, url_prefix='/api')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # テーブルを作成
        print("Database tables created successfully!")
    app.run(debug=True)
