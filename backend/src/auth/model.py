from sqlmodel import SQLModel

class Registrasi(SQLModel):
    username: str
    password: str
    full_name: str | None



class Token(SQLModel):
    access_token: str
    token_type: str = 'bearer'

