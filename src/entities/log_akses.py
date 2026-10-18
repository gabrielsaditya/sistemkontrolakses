from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, JSON
from datetime import datetime, timezone
import uuid

class TabelLogAkses(SQLModel, table=True):
    __tablename__ = "log_akses"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    id_pekerja: uuid.UUID = Field(
        foreign_key="pekerja.id",
        ondelete="RESTRICT"
    )
    uid_rfid: str
    nama_pekerja: str
    latensi_udara_masuk: float
    latensi_inferensi: float
    latensi_total: float
    tanggal_akses: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    item_terdeteksi: list[str] = Field(
        sa_column=Column(JSON, nullable=False)
    )
    keputusan: bool

    pekerja: "Pekerja" = Relationship(back_populates="log_akses")
    foto_raw_path: str
    foto_after_deteksi: str