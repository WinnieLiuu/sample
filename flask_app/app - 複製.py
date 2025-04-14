from flask import Flask, request, render_template, jsonify, redirect
from flask_restx import Api, Namespace, fields, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from threading import Thread
import sys
import signal
from fastapi_app import main  # 匯入 fastapi 啟動函式

app = Flask(__name__)
app.config["SWAGGER_UI_VERSION"] = "4.1.3"  # 這裡設定 Swagger UI 版本
app.config['JWT_SECRET_KEY'] = 'super-secret-key'  # 替換成自己的密鑰
jwt = JWTManager(app)

missions_dict = {}
time = {}

# 任務執行的函數
timecount = 0
def timed_job():
    global timecount
    if missions_dict:
        timecount += 1
        if timecount == 5:
            missions_dict[list(missions_dict.keys())[0]]["robot"] = 1
            missions_dict[list(missions_dict.keys())[0]]["status"] = "進行中"
        elif timecount == 10:
            missions_dict[list(missions_dict.keys())[0]]["status"] = "已完成"
        elif timecount == 12:
            timecount = 0
            del missions_dict[list(missions_dict.keys())[0]]
    else:
        timecount = 0

# 設置 APScheduler
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(timed_job, 'interval', seconds=1)  # 每5秒執行一次
    scheduler.start()

# 設定 PostgreSQL 連線
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin@localhost:5432/db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 創建 Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(50), nullable=False)

# 創建資料庫表
with app.app_context():
    db.create_all()

# user_api = Namespace("users", description="使用者API")
#
# @user_api.route("/")
# class UserResource(Resource):
#     def get(self):
#         users = User.query.all()
#         return [{'id': user.id, 'account': user.account, 'name': user.name, 'password': user.password} for user in users]
#
#     def post(self):
#         data = request.get_json()
#         account = data.get('account')
#         print(data['name'])
#         if not account:
#             return {"error": f"❌ 使用者 【{account}】 未輸入"}, 400
#         new_user = User(account=data['account'], name=data['name'], password=data['password'])
#         db.session.add(new_user)
#         db.session.commit()
#         return {"message": f"✅ 使用者 【{account}】 已新增"}, 200
#
# @user_api.route("/<account>")
# class UserAccountResource(Resource):
#     def put(self, account):
#         user = db.session.query(User).filter_by(account=account).first()
#         if user:
#             data = request.get_json()
#             user.name = data['name']
#             user.password = data['password']
#             db.session.commit()
#         return {"message": f"✅ 使用者 【{account}】 已修改"}, 201
#
#     def delete(self, account):
#         user = db.session.query(User).filter_by(account=account).first()
#         if user:
#             db.session.delete(user)
#             db.session.commit()
#             return {"message": f"✅ 使用者 【{account}】 已刪除"}, 200
#         else:
#             return {"message": f"❌ 使用者 【{account}】 不存在"}, 404
#
# api.add_namespace(user_api, path='/users')
#
# mission_api = Namespace("missions", description="任務API")
#
# @mission_api.route("/")
# class MissionResource(Resource):
#     def get(self):
#         mission_list = []
#         for key,value in missions_dict.items():
#             mission_list.append({"id":key,"name":value["name"],"robot":value["robot"],"status":value["status"]})
#         return mission_list, 200
#
#     def post(self):
#         data = request.get_json()
#         missionname = data.get('missionname')
#         if not missionname:
#             return {"error": f"❌ 任務名稱 【{missionname}】 不存在"}, 400
#
#         now = datetime.now()
#         missionid = now.strftime("%Y%m%d%H%M%S")
#         missions_dict[missionid] = {"name":missionname,"robot":0,"status":"待分配"}
#         return {"message": f"✅ 任務 【{missionid}】 已新增"}, 200
#
# @mission_api.route("/<missionid>")
# class MissionResource(Resource):
#     def put(self, missionid):
#         missions_dict[missionid] = request.json
#         return {missionid: missions_dict[missionid]}
#
#     def delete(self, missionid):
#         if missionid in missions_dict:
#             del missions_dict[missionid]
#             return {"message": f"✅ 任務 【{missionid}】 已刪除"}
#         return {"message": f"❌ 任務 【{missionid}】 不存在"}, 404
#
# api.add_namespace(mission_api, path='/missions')
#
# login_api = Namespace("login", description="登入API")
# @login_api.route("/")
# class LoginResource(Resource):
#     def post(self):
#         data = request.get_json()
#         missionname = data.get('missionname')
#         if not missionname:
#             return {"error": f"❌ 任務名稱 【{missionname}】 不存在"}, 400
#
#         now = datetime.now()
#         missionid = now.strftime("%Y%m%d%H%M%S")
#         missions_dict[missionid] = {"name":missionname,"robot":0,"status":"待分配"}
#         return {"message": f"✅ 任務 【{missionid}】 已新增"}, 200
#
# api.add_namespace(login_api, path='/login/access-token')


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

@app.route("/login", methods = ['POST','GET'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        account = data.get('account')
        password = data.get('password')

        # 範例驗證（實務上請查資料庫）
        user = User.query.filter_by(account=account, password=password).first()
        if user:
            access_token = create_access_token(identity=account)
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({"msg": "帳號或密碼錯誤"}), 401
    else:
        return render_template("login.html", locals=locals())

@app.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user = get_jwt_identity()  # 獲取當前用戶
    print(current_user)
    return jsonify(logged_in_as=current_user), 200


def run_app():
    app.run(port=3000, debug=True, use_reloader=False)

# 处理 Ctrl+C 的信号
def signal_handler(sig, frame):
    print("捕捉到中斷信號，正在退出...")
    sys.exit(0)

if __name__ == "__main__":
    # 捕捉 SIGINT 信號
    signal.signal(signal.SIGINT, signal_handler)

    start_scheduler()  # 啟動定時任務

    t1 = Thread(target=run_app)
    t2 = Thread(target=main.start_fastapi)

    # 設定為 daemon 執行緒
    t1.daemon = True
    t2.daemon = True

    t1.start()
    t2.start()

    # 主執行緒等待（因為子執行緒為 daemon，當主執行緒退出時程序會自動結束）
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("收到 Ctrl+C，中斷程序。")
        sys.exit(0)
