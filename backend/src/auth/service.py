from sqlmodel import select
from ..core.db import SessionDep
from .model import Registrasi
from ..entities.user import User
from fastapi import HTTPException, Depends
from .helper.auth_security import AuthHelper
from fastapi.security import OAuth2PasswordRequestForm

class AuthService:
    def __init__(self, session: SessionDep):
        self.session = session

    def register(self, form: Registrasi):
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
                'access_token': token,
                'token_type': 'bearer'
            }
            
        except HTTPException:
            self.session.rollback() 
            raise

        except Exception as e:
            self.session.rollback()
            raise HTTPException(500, f'PROSES LOGIN GAGAL DILAKUKAN: {e}')

    def login(self, form: OAuth2PasswordRequestForm = Depends()):
        try:
            pekerja_terdaftar = self.session.exec(select(User).where(User.username == form.username)).first()

            if not pekerja_terdaftar:
                raise HTTPException(401, 'INVALID CREDENTIALS!')
            
            servis = AuthHelper()
            
            verifikasi_password = servis.verifikasi_password(form.password, pekerja_terdaftar.hashed_password)
            if not verifikasi_password:
                raise HTTPException(401, "INVALID CREDENTIALS")
            
            token = servis.buat_token_akses({
                'sub': form.username
            })

            return {
                'access_token': token,
                'token_type': 'bearer'
            }
        
        except HTTPException:
            self.session.rollback()
            raise

        except Exception as e:
            self.session.rollback()
            raise HTTPException(500, f'PROSES LOGIN GAGAL DILAKUKAN: {e}')
