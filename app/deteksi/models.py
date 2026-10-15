import uuid
from typing import List
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON
from datetime import datetime

class TabelKonfigurasiDeteksi(SQLModel, table=True):
    __tablename__ = "konfigurasi_deteksi"

    id: uuid.UUID = Field(default_factory=uuid.UUID, primary_key=True)
    model_path: str = "best.pt"
    image_size: int = 640
    iou: float = 0.45
    conf: float = 0.5
    classes: List[int] | None = Field(default=None, sa_column=Column(JSON))

class Konfigurasi(SQLModel):
    id: uuid.UUID | None
    model_path: str | None
    image_size: int | None
    iou: float | None
    conf: float | None
    classes: List[int] | None

class DeteksiRequest(SQLModel):
    uid_rfid: str | None
    timestamp_dari_esp: datetime | None    

class DeteksiResponse(SQLModel):
    is_akses: bool





