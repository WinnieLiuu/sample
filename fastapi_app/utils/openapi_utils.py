from fastapi.openapi.utils import get_openapi
from fastapi_app.main import app

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

def simplified_openapi():
    openapi_schema = get_openapi(
        title="RESTful API",
        version="1.0.0",
        description="請先透過右上角 Authorize 登入，即可解鎖完整 API 文件。",
        routes=[],
        tags=[]
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
