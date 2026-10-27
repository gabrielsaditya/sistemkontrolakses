from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, JSON
from datetime import datetime, timezone
from ..entities.pekerja import Pekerja
import uuid

"""
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

Pengukuran dilakukan dengan beberapa metrik:
- delay atau latensi request response
- latensi yolo atau inferensi
- konsumsi cpu dan ram server saat menjalankan flow inferensi
- akurasi flow sampai keputusan akhir membuka pintu akses
"""

class TabelLogAkses(SQLModel, table=True):
    __tablename__ = "log_akses"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    id_pekerja: uuid.UUID = Field(
        foreign_key="pekerja.id",
        ondelete="RESTRICT"
    )
    uid_rfid: str
    nama_pekerja: str
    tanggal_akses: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    item_terdeteksi: list[str] = Field(
        sa_column=Column(JSON, nullable=False)
    )

    path_gambar_raw: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSON, nullable=False)
    )

    path_gambar_terdeteksi: list[str] = Field(
    default_factory=list,
    sa_column=Column(JSON, nullable=False)
    )

    #size foto
    size_foto_raw: list[float] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    size_foto_terdeteksi: list[float] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))

    #keputusan akses 
    keputusan_akses: bool

    #latensi
    latensi_request: float
    latensi_inferensi_yolo: float
    latensi_total: float

    #cpu & ram usage
    pemakaian_cpu: float
    pemakaian_ram: float

    pekerja: "Pekerja" = Relationship(back_populates="log_akses")