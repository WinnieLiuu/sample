from fastapi import APIRouter, Request, HTTPException, Query, Path
from pydantic import BaseModel
from datetime import datetime

from flask_app.app import missions_dict

router = APIRouter(prefix="/missions", tags=["missions"])

class MissionModel(BaseModel):
    name: str
    robot: int = 0
    status: str = "待分配"

@router.get("/")
def get_missions():
    return [{"id": k, **v} for k, v in missions_dict.items()]

@router.post("/{missionname}")
def create_mission(
    missionname: str = Path(..., description="The name of mission")
):
    print(f'missionname: {missionname}')
    if not missionname:
        raise HTTPException(status_code=400, detail=f"❌ 任務名稱 【{missionname}】 不存在")
    mission_id = datetime.now().strftime("%Y%m%d%H%M%S")
    missions_dict[mission_id] = {"name":missionname,"robot":0,"status":"待分配"}
    return {"message": f"✅ 任務 【{mission_id}】 已新增"}

@router.put("/{missionid}")
def update_mission(missionid: str, mission: MissionModel):
    missions_dict[missionid] = mission.dict()
    return {missionid: missions_dict[missionid]}

@router.delete("/{missionid}")
def delete_mission(missionid: str):
    if missionid in missions_dict:
        del missions_dict[missionid]
        return {"message": f"✅ 任務 【{missionid}】 已刪除"}
    return {"message": f"❌ 任務 【{missionid}】 不存在"}
