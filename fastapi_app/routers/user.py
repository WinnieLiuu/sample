from fastapi import APIRouter, Request, HTTPException, Depends, Query, Path
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional
import sys
import os

# 加入 flask_app 上層路徑
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from flask_app.models import User
from flask_app.routes import app
from flask_app import db

# app = create_app()

router = APIRouter(prefix="/users", tags=["users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme)):
    if token != "dummy_token_for_admin":
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"username": "admin"}

@router.get("/", tags=["users"])
async def get_users(current_user: dict = Depends(get_current_user)):
    with app.app_context():
        users = User.query.all()
        return [{'id': user.id, 'account': user.account, 'name': user.name, 'password': user.password} for user in users]

@router.get("/{account}")
async def get_user_by_id(account: str, current_user: dict = Depends(get_current_user)):
    with app.app_context():
        user = db.session.query(User).filter_by(account=account).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
    return {"username": user.name, "account": user.account, "password":user.password}

@router.post("/")
def create_user(
    account: str = Query(..., description="The id of a user (will be used to login)"),
    name = Query(..., description="The authorization level of a user"),
    password = Query(..., description="The password of a user (will be used to login)")
):

    if not account:
        return {"error": f"❌ 使用者 【{account}】 未輸入"}, 400
    with app.app_context():
        new_user = User(account=account, name=name, password=password)
        db.session.add(new_user)
        db.session.commit()
    return {"message": f"✅ 使用者 【{account}】 已新增"}, 200

@router.put("/{account}")
def update_user(
    account: str = Path(..., description="The id of a user (will be used to login)"),
    name: Optional[str] = Query(None, description="The authorization level of a user"),
    password: Optional[str] = Query(None, description="The password of a user (will be used to login)")
):
    with app.app_context():
        user = db.session.query(User).filter_by(account=account).first()
        if user:
            if name is not None:
                user.name = name
            if password is not None:
                user.password =password
            db.session.commit()
    return {"message": f"✅ 使用者 【{account}】 已修改"}, 201

@router.delete("/{account}")
def delete_user(account: str, current_user: dict = Depends(get_current_user)):
    with app.app_context():
        user = db.session.query(User).filter_by(account=account).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return {"message": f"✅ 使用者 【{account}】 已刪除"}, 200
        else:
            return {"message": f"❌ 使用者 【{account}】 不存在"}, 404

