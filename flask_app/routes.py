# flask_app/routes.py
from flask import request, jsonify, render_template, redirect, session, url_for
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, decode_token
import jwt 
from flask_app import db
from flask_app.models import Users
from flask_app import create_app

flask_main = create_app()

SECRET_KEY = 'super-secret-key'

@flask_main.route("/index")
def index():
    # 從 session 中取得 token 與 username
    token = session.get('token')
    account = session.get('account')
    print(f'token: {token}, account: {account}')
    if not token or not account:
        return redirect(url_for('login'))
    return render_template("index.html")

@flask_main.route("/mission")
def mission():
    # 從 session 中取得 token 與 username
    token = session.get('token')
    account = session.get('account')
    if not token or not account:
        return redirect(url_for('index'))
    return render_template("mission.html")

@flask_main.route("/history")
def mission_history():
    # 從 session 中取得 token 與 username
    token = session.get('token')
    account = session.get('account')
    if not token or not account:
        return redirect(url_for('index'))
    return render_template("mission_history.html")

@flask_main.route("/user")
def user():
    # 從 session 中取得 token 與 username
    token = session.get('token')
    account = session.get('account')
    if not token or not account:
        return redirect(url_for('login'))
    return render_template("user.html")

@flask_main.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        account = data.get('account')
        password = data.get('password')

        user = Users.query.filter_by(account=account, password=password).first()
        if user:
            # 使用 Flask-JWT-Extended 建立 access token
            access_token = create_access_token(identity=account)
            
            # 將 token 與 username 存入 session
            session['token'] = access_token
            session['account'] = account
            session['name'] = user.name
            return jsonify(access_token=access_token, logged_in_as=user.name), 200
        else:
            return jsonify({"msg": "帳號或密碼錯誤"}), 401
    else:
        # 從 session 中取得 token 與 username
        token = session.get('token')
        account = session.get('account')
        if not token or not account:
            return render_template("login.html")
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            if payload.get("sub") != account:
                raise jwt.InvalidTokenError("帳號不符")

        except jwt.ExpiredSignatureError:
            print("⚠️ Token 過期")
            return render_template("login.html")
        except jwt.InvalidTokenError:
            print("⚠️ Token 無效")
            return render_template("login.html")

        return redirect(url_for('index'))
    
@flask_main.route('/logout')
def logout():
    session.clear()  # 清除所有 session 資料
    return redirect(url_for('login'))  # 導回登入頁

@flask_main.route('/flask-protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200
