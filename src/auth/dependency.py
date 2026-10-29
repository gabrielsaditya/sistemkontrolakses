import secrets
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import JWTError, jwt
from ..core.config import SECRET_KEY, ALGORITHM, OAUTH2_SCHEME, ESP_32_API_KEY
from sqlmodel import select
from fastapi import Depends, HTTPException
from ..entities.user import User
from ..core.db import SessionDep

#jwt

def get_current_user(session: SessionDep, token: str = Depends(OAUTH2_SCHEME)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise HTTPException(401, 'TOKEN PAYLOAD TIDAK VALID')
    except JWTError:
        raise HTTPException(401, 'TOKEN TIDAK VALID')

    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise HTTPException(404, 'USER TIDAK DITEMUKAN')
    return user

#cek user_role
def require_role(role: str):
    def decorator(user: User = Depends(get_current_user)):
        if user.role != role:
            raise HTTPException(403, 'FORBIDDEN')
        return user
    return decorator

#API key perangkat
device_key_header = APIKeyHeader(
    name='X-Device-Key',
    auto_error=False
)

def verifikasi_perangkat(
        api_key: str | None = Depends(device_key_header)
):
    if not api_key or not secrets.compare_digest(
        api_key, ESP_32_API_KEY
    ):
        raise HTTPException(401, 'KREDENSIAL PERANGKAT TIDAK VALID')

    return True
    