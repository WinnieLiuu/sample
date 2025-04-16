from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import uvicorn
import jwt
from jwt import PyJWTError

import importlib.util
from pathlib import Path

from .routers.auth import verify_token

# === Tag metadata ===
tags_metadata = [
    {
        "name": "users",
        "description": "查詢所有用戶或特定用戶資訊。",
    },
    {
        "name": "missions",
        "description": "查詢所有任務資訊。",
    },
]

# === App 初始化 ===
fastapi_main = FastAPI(
    docs_url=None,         # 關閉內建 /docs
    redoc_url=None,        # 關閉 /redoc
    openapi_url="/openapi.json",  # 可自訂 openapi 路由（保留）
)

# 若你從前端測試，需啟用 CORS（Swagger 內建不需要）
fastapi_main.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === 路由清單集中管理 ===
# 定義 router 資料夾路徑
routers_dir = Path(__file__).parent / "routers"

# 取得 routers 資料夾中的所有 .py 檔案（排除 __init__.py）
router_files = [f for f in os.listdir(routers_dir) if f.endswith(".py") and f != "__init__.py"]

# 動態加載每個 router 檔案
for file in router_files:
    module_name = file[:-3]  # 去掉 .py 副檔名
    module_path = routers_dir / file

    # 動態載入模組
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # 假設每個模組有一個名為 router 的變數 (FastAPI Router 物件)
    if hasattr(module, 'router'):
        fastapi_main.include_router(module.router)

# === 自定義 OpenAPI ===
def simplified_openapi():
    openapi_schema = get_openapi(
        title="RESTful API",
        version="1.0.0",
        description="請先透過右上角 Authorize 登入，即可解鎖完整 API 文件。",
        routes=[],
        tags=[]
    )

    # ✅ 強制加入 securitySchemes → 顯示 Authorize 按鈕
    # 確保 openapi_schema 是有效的
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}

    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/login/access-token",
                    "scopes": {}
                }
            }
        }
    }

    openapi_schema["security"] = [{"OAuth2PasswordBearer": []}]
    return openapi_schema

def full_openapi():
    openapi_schema = get_openapi(
        title="RESTful API",
        version="1.0.0",
        description="登入後可使用所有功能。",
        routes=[route for route in app.routes if "/logout" not in route.path and "/login" not in route.path],
        tags=[tag for tag in tags_metadata if tag["name"] not in ["login","logout"]]
    )

    if "components" not in openapi_schema:
        openapi_schema["components"] = {}

    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/login/access-token",
                    "scopes": {}
                }
            }
        }
    }

    openapi_schema["security"] = [{"OAuth2PasswordBearer": []}]
    return openapi_schema

# 取得目前檔案所在資料夾
BASE_DIR = os.path.dirname(__file__)

# 靜態資料夾位置
static_path = os.path.join(BASE_DIR, "static")
fastapi_main.mount("/static", StaticFiles(directory=static_path), name="static")

@fastapi_main.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    file_path = os.path.join(static_path, "swagger-ui.html")
    return FileResponse(file_path)

# 初始顯示簡化版文件
fastapi_main.openapi_schema = simplified_openapi()
fastapi_main.openapi = lambda: fastapi_main.openapi_schema

def start_fastapi():
    uvicorn.run(fastapi_main, host="127.0.0.1", port=3000)

# === 測試入口 ===
if __name__ == "__main__":
    uvicorn.run("app:fastapi_main", host="127.0.0.1", port=3000, reload=True)
