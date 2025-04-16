from fastapi import APIRouter
from fastapi import Request
from fastapi_app.utils.openapi_utils import simplified_openapi

router = APIRouter(prefix="/api/logout", tags=["logout"])

@router.post("/")
async def logout(request: Request):
    # ✅ 透過 request.app 存取 app 實例並動態更改 schema
    request.app.openapi_schema = simplified_openapi()
    return {"message": "已登出，openapi schema 已重設"}