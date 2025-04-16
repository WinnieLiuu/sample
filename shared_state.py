# shared_state.py
from threading import Lock

missions_dict = {}  # 共用任務字典
missions_lock = Lock()

def update_missions(key, value):
    with missions_lock:
        if key not in missions_dict:
            missions_dict[key] = value
        else:
            for k, v in value.items():
                missions_dict[key][k] = v

def delete_mission(key):
    with missions_lock:
        if key in missions_dict:
            del missions_dict[key]