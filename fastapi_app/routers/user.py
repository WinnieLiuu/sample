from fastapi import APIRouter, Request, HTTPException, Depends, Query, Path
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import sys
import os

from fastapi_app.routers.auth import verify_token

# 加入 flask_app 上層路徑
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from flask_app.models import Users
from flask_app.routes import flask_main
from flask_app import db

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("", tags=["users"])
async def get_users(current_user: str = Depends(verify_token)):
    with flask_main.app_context():
        users = db.session.query(Users).all()
        return [{'id': user.id, 'account': user.account, 'name': user.name, 'password': user.password} for user in users]

@router.post("/checkuser")
async def get_user_by_id(userdata: dict, current_user: str = Depends(verify_token)):
    data = userdata.get("data")
    msg = "使用者已存在"
    with flask_main.app_context():
        user = db.session.query(Users).filter_by(account=data.get("account")).first()
        if user is None:
            msg = "使用者不存在"
    return JSONResponse(
        content={"message": msg},
        status_code=200
    )

@router.post("")
def create_user(
    account: str = Query(..., description="The id of a user (will be used to login)"),
    name = Query(..., description="The authorization level of a user"),
    password = Query(..., description="The password of a user (will be used to login)"),
    current_user: str = Depends(verify_token)
):

    if not account:
        return {"error": f"❌ 使用者 【{account}】 未輸入"}, 400
    with flask_main.app_context():
        new_user = Users(account=account, name=name, password=password)
        db.session.add(new_user)
        db.session.commit()
    return JSONResponse(
        content={"message": f"✅ 使用者 【{account}】 已新增"},
        status_code=200
    )

@router.put("/{account}")
def update_user(
    account: str = Path(..., description="The id of a user (will be used to login)"),
    name: Optional[str] = Query(None, description="The authorization level of a user"),
    password: Optional[str] = Query(None, description="The password of a user (will be used to login)"),
    current_user: str = Depends(verify_token)
):
    with flask_main.app_context():
        user = db.session.query(Users).filter_by(account=account).first()
        if user:
            if name is not None:
                user.name = name
            if password is not None:
                user.password =password
            db.session.commit()
    return JSONResponse(
        content={"message": f"✅ 使用者 【{account}】 已修改"},
        status_code=200
    )

@router.delete("/{account}")
def delete_user(account: str, current_user: str = Depends(verify_token)):
    with flask_main.app_context():
        user = db.session.query(Users).filter_by(account=account).first()
        if user:
            if user.account == "admin":
                return JSONResponse(
                    content={"message": "❌ 管理員帳號不能刪除"},
                    status_code=400
                )
            db.session.delete(user)
            db.session.commit()
            return JSONResponse(
                content={"message": f"✅ 使用者 【{account}】 已刪除"},
                status_code=200
            )
        else:
            return JSONResponse(
                content={"message": f"❌ 使用者 【{account}】 不存在"},
                status_code=404
            )

