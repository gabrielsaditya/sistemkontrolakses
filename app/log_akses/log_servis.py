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
    pekerja_id: Optional[uuid.UUID] = None,
    pekerja_nama: Optional[str] = None,
    rfid_uid: Optional[str] = None,
    alasan: Optional[str] = None,
    foto_raw_path: Optional[str] = None,
    foto_annotated_path: Optional[str] = None,
    ukuran_foto_raw: Optional[int] = None,
    ukuran_foto_annotated: Optional[int] = None,
    latensi_1: Optional[float] = None,
    latensi_2: Optional[float] = None,
    latensi_3: Optional[float] = None,
    latensi_4: Optional[float] = None,
    latensi_total: Optional[float] = None,
    latensi_udara: Optional[float] = None,
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