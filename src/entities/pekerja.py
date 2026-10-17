import uuid
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel

class Pekerja(SQLModel, table=True):
    __tablename__ = 'pekerja'
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    name: str = Field(index=True, unique=True)
    rfid_uid: str = Field(index=True, unique=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    role: str
    is_active: bool = Field(default=True)
