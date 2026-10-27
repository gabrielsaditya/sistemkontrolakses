from fastapi import HTTPException, APIRouter
from .service import AuthService
from ..core.db import SessionDep
from .model import Token, Registrasi, Login


router = APIRouter(prefix='/auth', tags=['auth'])

@router.post('/register', response_model=Token)
def daftar_user_baru(session: SessionDep,form: Registrasi):
    try: 
        servis = AuthService(session)
        return servis.register(form)
    except Exception as e:
        raise HTTPException(505, f'PROSES REGISTER GAGAL DILAKUKAN')


@router.post('/login', response_model=Token)
def login(session: SessionDep, form: Login):
    try:
        servis = AuthService(session)
        return servis.login(form)
    except Exception as e:
        raise HTTPException(505, f'GAGAL LOGIN USER: {e}')
        