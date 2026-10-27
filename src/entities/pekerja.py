from sqlmodel import Field, SQLModel, Relationship
from ..entities.log_akses import TabelLogAkses
from datetime import datetime, timezone
import uuid

class Pekerja(SQLModel, table=True):
    __tablename__ = "pekerja"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True, unique=True)
    rfid_uid: str = Field(index=True, unique=True)
    role: str
    is_active: bool = Field(default=True)
    log_akses: list["TabelLogAkses"] = Relationship(
        back_populates="pekerja"
    )