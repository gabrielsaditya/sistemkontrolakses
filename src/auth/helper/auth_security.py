from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from ...core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

class AuthHelper:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
        self.load_environment()

    def load_environment(self):
        self.SECRET_KEY = SECRET_KEY
        self.ALGORITHM = ALGORITHM
        self.ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES

        if not self.SECRET_KEY or not self.ALGORITHM:
            raise RuntimeError("KONFIGURASI AUTENTIKASI BELUM LENGKAP")


    def hash_password(self, password_asal: str):
        return self.pwd_context.hash(password_asal)

    def verifikasi_password(self, password_asal, password_ter_hashed):
        return self.pwd_context.verify(password_asal,password_ter_hashed)

    def buat_token_akses(self, data: dict):
        try:
            expire = datetime.now(timezone.utc) + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
            to_encode = data.copy()
            to_encode.update({'exp': expire})
            return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        except JWTError as e:
            raise RuntimeError("SIGN JWT GAGAL DILAKUKAN: {e}") 