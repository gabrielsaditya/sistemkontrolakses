import uuid
from typing import List
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON
from datetime import datetime
from fastapi import Form

#TABEL KONFIGURASI
class TabelKonfigurasiDeteksi(SQLModel, table=True):
    __tablename__ = "konfigurasi_deteksi"

    id: uuid.UUID = Field(default_factory=uuid.UUID, primary_key=True)
    model_path: str = "best.pt"
    image_size: int = 640
    iou: float = 0.45
    conf: float = 0.5
    classes: List[int] | None = Field(default=None, sa_column=Column(JSON))


#DTO - HTTP -> DATA REQUEST DAN RESPONSE
class Konfigurasi(SQLModel):
    id: uuid.UUID | None
    model_path: str | None
    image_size: int | None
    iou: float | None
    conf: float | None
    classes: List[int] | None

class DeteksiRequest(SQLModel):
    device_id: str = Form(...)
    uid_rfid: str = Form(...)
    timestamp_dari_esp: str = Form(...)   

class DeteksiResponse(SQLModel):
    keputusan_akses: bool
    nama_pekerja: str
    alasan: str
    timestamp: datetime





