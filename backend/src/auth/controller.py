from fastapi import HTTPException, APIRouter, Depends
from .service import AuthService
from ..core.db import SessionDep
from .model import Token, Registrasi
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix='/auth', tags=['auth'])

@router.post('/register', response_model=Token)
def daftar_user_baru(session: SessionDep,form: Registrasi):
    return AuthService(session).register(form)


@router.post('/login', response_model=Token)
def login(session: SessionDep, form: OAuth2PasswordRequestForm = Depends()):
    return AuthService(session).login(form)
        