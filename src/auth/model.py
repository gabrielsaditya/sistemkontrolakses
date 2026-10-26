from sqlmodel import SQLModel

class Registrasi(SQLModel):
    username: str
    password: str
    full_name: str | None

class Login(SQLModel):
    username: str
    password: str

class UserPublic(SQLModel):
    username: str
    full_name: str | None

class Token(SQLModel):
    token_akses: str
    tipe_token: str = 'bearer'

