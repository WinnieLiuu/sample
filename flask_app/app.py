from flask_app.routes import app  # Flask 應用
from apscheduler.schedulers.background import BackgroundScheduler
from threading import Thread
import sys
import signal
from fastapi_app import main as fastapi_main  # FastAPI 應用
from shared_state import missions_dict, update_missions, delete_mission

timecount = 0

# 模擬任務流程
def timed_job():
    global timecount
    if missions_dict:
        timecount += 1
        keys = list(missions_dict.keys())
        if timecount == 5:
            update_missions(keys[0], {"robot": 1, "status": "進行中"})
        elif timecount == 10:
            update_missions(keys[0], {"status": "已完成"})
        elif timecount == 12:
            timecount = 0
            delete_mission(keys[0])
    else:
        timecount = 0
    print(f'timecount: {timecount}')

# 啟動 APScheduler
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(timed_job, 'interval', seconds=1)
    scheduler.start()
    print("✅ APScheduler 已啟動")

# 執行 Flask
def run_app():
    app.run(port=3000, debug=True, use_reloader=False)

# Ctrl+C 結束程序
def signal_handler(sig, frame):
    print("✅ APScheduler 已停止")
    sys.exit(0)

# 程式主入口
if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    start_scheduler()

    t1 = Thread(target=run_app, daemon=True)                  # 啟動 Flask
    t2 = Thread(target=fastapi_main.start_fastapi, daemon=True)  # 啟動 FastAPI

    t1.start()
    t2.start()
    print("✅ 所有服務已啟動")

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("✅ APScheduler 已停止")
        sys.exit(0)
