from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt import PyJWTError, ExpiredSignatureError

SECRET_KEY = 'super-secret-key'
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/access-token")

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        account: str = payload.get("sub")
        if account is None:
            raise HTTPException(
                status_code=401,
                detail="Token payload error",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return account
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate token",
            headers={"WWW-Authenticate": "Bearer"},
        )
