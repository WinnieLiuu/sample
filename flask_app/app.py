from flask_app.routes import app  # Flask 應用
from apscheduler.schedulers.background import BackgroundScheduler
from threading import Thread
import sys
import signal
from fastapi_app import main as fastapi_main  # FastAPI 應用
# from flask_app import create_app

missions_dict = {}  # 共用任務字典
timecount = 0

# app = create_app()

missions_dict = {}
timecount = 0

# 模擬任務流程
def timed_job():
    global timecount
    if missions_dict:
        timecount += 1
        keys = list(missions_dict.keys())
        if timecount == 5:
            missions_dict[keys[0]]["robot"] = 1
            missions_dict[keys[0]]["status"] = "進行中"
        elif timecount == 10:
            missions_dict[keys[0]]["status"] = "已完成"
        elif timecount == 12:
            timecount = 0
            del missions_dict[keys[0]]
    else:
        timecount = 0

# 啟動 APScheduler
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(timed_job, 'interval', seconds=1)
    scheduler.start()

# 執行 Flask
def run_app():
    app.run(port=3000, debug=True, use_reloader=False)

# Ctrl+C 結束程序
def signal_handler(sig, frame):
    print("捕捉到中斷信號，正在退出...")
    sys.exit(0)

# 程式主入口
if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    start_scheduler()

    t1 = Thread(target=run_app, daemon=True)                  # 啟動 Flask
    t2 = Thread(target=fastapi_main.start_fastapi, daemon=True)  # 啟動 FastAPI

    t1.start()
    t2.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("收到 Ctrl+C，中斷程序。")
        sys.exit(0)
