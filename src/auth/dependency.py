from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv('.env')
SECRET_KEY = os.getenv('SECRET_KEY') 
ALGORITHM = os.getenv('ALGORITHM')

print(BASE_DIR)
print(SECRET_KEY)
print(ALGORITHM)
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session, select
from fastapi import Depends, HTTPException
from ..entities.user import User
from ..core.db import SessionDep


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')
def get_current_user(session: SessionDep, token: str = Depends(oauth2_scheme)):
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

def require_role(role: str):
    def decorator(user: User = Depends(get_current_user)):
        if user.role != role:
            raise HTTPException(403, 'FORBIDDEN')
        return user
    return decorator

