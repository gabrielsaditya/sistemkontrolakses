import uuid
from datetime import datetime, timezone
from typing import List
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON


class LogAkses(SQLModel, table=True):
    __tablename__ = "log_akses"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        index=True,
    )
    pekerja_id: uuid.UUID | None = Field(default=None, foreign_key="pekerja.id")
    pekerja_nama: str | None = None
    rfid_uid: str | None = None
    keputusan: bool
    alasan: str | None = None
    detections: List[dict] = Field(default_factory=list, sa_column=Column(JSON))

    # path file foto
    foto_raw_path: str | None = None
    foto_annotated_path: str | None = None

    # ukuran file (bytes)
    ukuran_foto_raw: int | None = None
    ukuran_foto_annotated: int | None = None
    ukuran_foto_total: int | None = None

    # latensi (ms)
    latensi_1: float | None = None
    latensi_2: float | None = None
    latensi_3: float | None = None
    latensi_4: float | None = None
    latensi_total: float | None = None
    latensi_udara: float | None = None

