from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from fastapi_app.utils.openapi_utils import full_openapi

router = APIRouter(prefix="/login/access-token", tags=["login"])

missions_dict = {}

@router.post("/")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), request: Request = None):
    if form_data.username != "admin" or form_data.password != "admin":
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    request.app.openapi_schema = full_openapi()
    return {
        "access_token": "dummy_token_for_admin",
        "token_type": "bearer"
    }
    

