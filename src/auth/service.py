from sqlmodel import Session, select
from ...src.core.db import SessionDep
from .model import Registrasi, Login
from ..entities.user import User
from fastapi import HTTPException, status, Depends
from .helper.auth_security import AuthHelper
from dotenv import load_dotenv
from pathlib import Path
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import os

BASE_DIR = Path(__file__).resolve.parents[2]
load_dotenv(BASE_DIR / '.env')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')

if not SECRET_KEY and not ALGORITHM:
    raise HTTPException(404, 'SECRET_KEY DAN ALGORITHM TIDAK DITEMUKAN')

class AuthService:
    def __init__(self, session: SessionDep):
        self.session = session

    def register(self, form: Registrasi):
        #cari pekerja dulu
        try:
            db_user = self.session.exec(select(User).where(form.username == User.username)).first()

            if db_user:
                raise HTTPException(404, 'PEKERJA TELAH TERDAFTAR!')
            service = AuthHelper()
            password_hashed = service.hash_password(form.password)
            data_user_baru = User(
                username = form.username,
                hashed_password = password_hashed,
            )
            
            self.session.add(data_user_baru)
            self.session.commit()
            self.session.refresh(data_user_baru)

            #buat token akses
            
            token = service.buat_token_akses({
                'sub': form.username
            })


            return {
                'token_akses': token,
                'tipe_token': 'bearer'
            }
            
        except HTTPException:
            raise

        except Exception as e:
            raise HTTPException(500, 'PROSES LOGIN GAGAL DILAKUKAN')

    def login(self, form: Login):
        try:
            pekerja_terdaftar = self.session.exec(select(User).where(User.username == form.username)).first()

            if not pekerja_terdaftar :
                raise HTTPException(401, 'INVALID CREDENTIALS!')
            
            servis = AuthHelper()
            
            verifikasi_password = servis.verifikasi_password(form.password, pekerja_terdaftar.hashed_password)
            if not verifikasi_password:
                raise HTTPException(401, "INVALID CREDENTIALS")
            
            token = servis.buat_token_akses({
                'sub': form.username
            })

            return {
                'token_akses': token,
                'tipe_token': 'bearer'
            }


        except HTTPException:
            raise

        except Exception as e:
            raise HTTPException(500, f'PROSES LOGIN GAGAL DILAKUKAN: {e}')
