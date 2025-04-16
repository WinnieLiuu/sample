from flask_app.routes import flask_main  # Flask 應用
from fastapi.middleware.wsgi import WSGIMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from threading import Thread
import sys
import signal
from fastapi_app.app import fastapi_main  # FastAPI 應用
from shared_state import missions_dict, update_missions, delete_mission
import uvicorn

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
    flask_main.run(port=3000, debug=True, use_reloader=False)

# Ctrl+C 結束程序
def signal_handler(sig, frame):
    print("✅ APScheduler 已停止")
    sys.exit(0)

# 程式主入口
if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    start_scheduler()
    # 掛載 Flask 應用到 FastAPI (此例會將所有 /hello_flask 的請求轉給 Flask 處理)
    fastapi_main.mount("/flask", WSGIMiddleware(flask_main))

    # 若在本地測試，可啟動 Uvicorn
    uvicorn.run(fastapi_main, host="127.0.0.1", port=8000)
    print("✅ 所有服務已啟動")
