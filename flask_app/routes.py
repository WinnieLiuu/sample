# flask_app/routes.py
from flask import request, jsonify, render_template, redirect, session
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_app import db
from flask_app.models import Users
from flask_app import create_app

app = create_app()

@app.route("/")
def redirect_to_index():
    return redirect("index")

@app.route("/index")
def index():
    # 從 session 中取得 token 與 username
    token = session.get('token')
    account = session.get('account')
    if not token or not account:
        return redirect('login')
    return render_template("index.html")

@app.route("/mission")
def mission():
    # 從 session 中取得 token 與 username
    token = session.get('token')
    account = session.get('account')
    if not token or not account:
        return redirect('index')
    return render_template("mission.html")

@app.route("/user")
def user():
    # 從 session 中取得 token 與 username
    token = session.get('token')
    account = session.get('account')
    if not token or not account:
        return redirect('login')
    return render_template("user.html")

@app.route("/login", methods=['POST', 'GET'])
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
        else:
            return redirect('index')
    
@app.route('/logout')
def logout():
    session.clear()  # 清除所有 session 資料
    return redirect('login')  # 導回登入頁

@app.route('/flask-protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200
