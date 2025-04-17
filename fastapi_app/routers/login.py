from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt

from fastapi_app.utils.openapi_utils import full_openapi

router = APIRouter(prefix="/login/access-token", tags=["login"])

# JWT 設定
SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 建立 token 的工具函式
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
@router.get("/")
def root():
    return {"status": "ok"}

@router.post("/")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), request: Request = None):
    if form_data.username != "admin" or form_data.password != "admin":
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    request.app.openapi_schema = full_openapi()

    access_token = create_access_token(data={"sub": form_data.username})
    print(f'access_token:{access_token}')

    return {
        "logged_in_as": form_data.username,
        "access_token": access_token,
        "token_type": "bearer"
    }

