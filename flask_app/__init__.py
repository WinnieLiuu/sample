# flask_app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# 初始化資料庫物件（稍後與 app 綁定）
db = SQLAlchemy()
jwt = JWTManager()


def create_app():    
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin@localhost:5432/db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'super-secret-key'

    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        from . import models
        db.create_all()

    return app

