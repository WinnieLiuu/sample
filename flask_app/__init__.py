# flask_app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import datetime
import os
from sqlalchemy import create_engine

# 初始化資料庫物件（稍後與 app 綁定）
db = SQLAlchemy()
jwt = JWTManager()


def create_app():    
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'  # 用於 Session

    CORS(app, supports_credentials=True)

    ENV = os.getenv("ENVIRONMENT", "local")

    if ENV == "render":
        # deploy to render
        DATABASE_URL = os.environ.get("DATABASE_URL")
        engine = create_engine(DATABASE_URL)
    else:
        # local
        DATABASE_URL = 'postgresql://admin:admin@localhost:5432/db'

    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["SQLALCHEMY_ECHO"] = True
    app.config['JWT_SECRET_KEY'] = 'super-secret-key'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(minutes=30)

    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        from . import models
        db.create_all()

        # ✅ 檢查是否已有 admin 帳號，避免重複新增
        from flask_app.models import Users
        if not Users.query.filter_by(account="admin").first():
            admin_user = Users(
                account="admin",
                name="admin",
                password="admin"  # 你也可以用 hash 加密
            )
            db.session.add(admin_user)
            db.session.commit()
            print("✅ 已新增 admin 使用者")
        else:
            print("ℹ️ admin 使用者已存在，略過建立")
    return app

