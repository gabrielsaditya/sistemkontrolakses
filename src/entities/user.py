from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
import uuid

if TYPE_CHECKING:
    from .konfigurasi_deteksi import TabelKonfigurasiDeteksi

class User(SQLModel, table=True):
    __tablename__ = "user"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(min_length=6, max_length=20, unique=True, index=True)
    hashed_password: str = Field(min_length=6)
    role: str = Field(default="user")

    konfigurasi_deteksi: 'TabelKonfigurasiDeteksi' =Relationship(back_populates='user')
    
        