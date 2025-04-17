from fastapi import APIRouter, Request, HTTPException, Query, Path, Depends
from pydantic import BaseModel
from datetime import datetime

from shared_state import missions_dict
from fastapi_app.routers.auth import verify_token
import sys
import os

# 加入 flask_app 上層路徑
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from flask_app.models import Missions
from flask_app.routes import flask_main
from flask_app import db

router = APIRouter(prefix="/api/missions", tags=["missions"])

class MissionModel(BaseModel):
    name: str
    robot: int = 0
    status: str = "待分配"

@router.get("")
def get_missions(current_user: str = Depends(verify_token)):
    return [{"id": k, **v} for k, v in missions_dict.items()]

@router.get("/history")
def get_missions(current_user: str = Depends(verify_token)):
    with flask_main.app_context():
        missions = db.session.query(Missions).all()
        return [{'id': mission.id, 'missionId': mission.missionId, 'missionName': mission.missionName, 'robot': mission.robot, 'missionStatus': mission.missionStatus, 'startTime': mission.startTime, 'finishTime': mission.finishTime} for mission in missions]
    
@router.post("/{missionname}")
def create_mission(
    missionname: str = Path(..., description="The name of mission"), current_user: str = Depends(verify_token)
):
    print(f'missionname: {missionname}')
    if not missionname:
        raise HTTPException(status_code=400, detail=f"❌ 任務名稱 【{missionname}】 不存在")
    mission_id = datetime.now().strftime("%Y%m%d%H%M%S")
    missions_dict[mission_id] = {"missionName":missionname,"robot":0,"missionStatus":"待分配"}

    return {"message": f"✅ 任務 【{mission_id}】 已新增"}

@router.put("")
def update_mission(mission: dict, current_user: str = Depends(verify_token)):
    print(f'data_get: {mission}')
    datas = mission.get("data")
    missions_dict.clear()
    for data in datas:
        missions_dict[data["id"]] = data
    print(f'missions_dict: {missions_dict}')
    return {"message": f"✅ 任務已修改"}

@router.delete("/{missionid}")
def delete_mission(missionid: str, current_user: str = Depends(verify_token)):
    if missionid in missions_dict:

        with flask_main.app_context():
            new_mission = Missions(missionId=missionid, missionName=missions_dict[missionid]["missionName"], robot=missions_dict[missionid]["robot"], missionStatus="已取消", startTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), finishTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            db.session.add(new_mission)
            db.session.commit()

        del missions_dict[missionid]
        return {"message": f"✅ 任務 【{missionid}】 已刪除"}
    return {"message": f"❌ 任務 【{missionid}】 不存在"}
