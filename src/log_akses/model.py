from sqlmodel import SQLModel
import uuid
from datetime import datetime

class CreateLog(SQLModel):
    uid_rfid: str
    nama_pekerja: str
    tanggal_akses: datetime
    item_terdeteksi: list[str]
    path_gambar_raw: list[str]
    path_gambar_terdeteksi: list[str]
    size_foto_raw: list[float]
    size_foto_terdeteksi: list[float]
    keputusan_akses: bool
    latensi_request: float
    latensi_inferensi_yolo: float
    latensi_total: float
    pemakaian_cpu: float
    pemakaian_ram: float 

class ReadLog(SQLModel):
    id: uuid.UUID
    id_pekerja: uuid.UUID
    uid_rfid: str
    nama_pekerja: str
    tanggal_akses: datetime
    item_terdeteksi: list[str]
    path_gambar_raw: list[str]
    path_gambar_terdeteksi: list[str]
    size_foto_raw: list[float]
    size_foto_terdeteksi: list[float]
    keputusan_akses: bool
    latensi_request: float
    latensi_inferensi_yolo: float
    latensi_total: float
    pemakaian_cpu: float
    pemakaian_ram: float

class UpdateLog(SQLModel):
    uid_rfid: str | None
    nama_pekerja: str | None
    tanggal_akses: datetime | None
    item_terdeteksi: list[str] | None
    path_gambar_raw: list[str] | None
    path_gambar_terdeteksi: list[str] | None
    size_foto_raw: list[float] | None
    size_foto_terdeteksi: list[float] | None
    keputusan_akses: bool | None
    latensi_request: float | None
    latensi_inferensi_yolo: float | None
    latensi_total: float | None
    pemakaian_cpu: float | None
    pemakaian_ram: float | None
