# flask_app/routes.py
from flask import request, jsonify, render_template, redirect
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_app import db
from flask_app.models import User
from flask_app import create_app

app = create_app()

missions_dict = {}
timecount = 0

@app.route("/")
def redirect_to_index():
    return redirect("index")

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/mission")
def mission():
    return render_template("mission.html")

@app.route("/user")
def user():
    return render_template("user.html")

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        account = data.get('account')
        password = data.get('password')

        user = User.query.filter_by(account=account, password=password).first()
        if user:
            access_token = create_access_token(identity=account)
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({"msg": "帳號或密碼錯誤"}), 401
    else:
        return render_template("login.html")

@app.route('/flask-protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200
