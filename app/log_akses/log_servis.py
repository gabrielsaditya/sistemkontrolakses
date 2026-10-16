# app/log/service.py (atau service/log_service.py)
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlmodel import Session
from app.log_akses.models import LogAkses


def simpan_log(
    session: Session,
    *,
    keputusan: bool,
    detections: List[dict],
    pekerja_id: uuid.UUID | None = None,
    pekerja_nama: str | None = None,
    rfid_uid: str | None = None,
    alasan: str | None = None,
    foto_raw_path: str | None = None,
    foto_annotated_path: str | None = None,
    ukuran_foto_raw: int | None = None,
    ukuran_foto_annotated: int | None = None,
    latensi_1: float | None = None,
    latensi_2: float | None = None,
    latensi_3: float | None = None,
    latensi_4: float | None = None,
    latensi_total: float | None = None,
    latensi_udara: float | None = None,
) -> LogAkses:
    ukuran_total = None
    if ukuran_foto_raw is not None or ukuran_foto_annotated is not None:
        ukuran_total = (ukuran_foto_raw or 0) + (ukuran_foto_annotated or 0)

    log = LogAkses(
        keputusan=keputusan,
        detections=detections,
        pekerja_id=pekerja_id,
        pekerja_nama=pekerja_nama,
        rfid_uid=rfid_uid,
        alasan=alasan,
        foto_raw_path=foto_raw_path,
        foto_annotated_path=foto_annotated_path,
        ukuran_foto_raw=ukuran_foto_raw,
        ukuran_foto_annotated=ukuran_foto_annotated,
        ukuran_foto_total=ukuran_total,
        latensi_1=latensi_1,
        latensi_2=latensi_2,
        latensi_3=latensi_3,
        latensi_4=latensi_4,
        latensi_total=latensi_total,
        latensi_udara=latensi_udara,
    )

    try:
        session.add(log)
        session.commit()
        session.refresh(log)
        return log
    except Exception as e:
        session.rollback()
        raise RuntimeError(f"GAGAL SIMPAN LOG: {e}")