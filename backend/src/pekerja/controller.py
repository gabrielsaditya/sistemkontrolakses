import uuid
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from ..core.db import SessionDep
from .model import (
    PekerjaCreate,
    PekerjaRead,
    PekerjaUpdate,
    RFIDScan
)
from .service import PekerjaService
from ..auth.dependency import require_role
from ..auth.dependency import verifikasi_perangkat

router = APIRouter(prefix="/pekerja", tags=['pekerja'], dependencies=[Depends(require_role("admin"))])

@router.post("/", response_model=PekerjaRead, status_code=status.HTTP_201_CREATED)
def tambah_pekerja(session: SessionDep, form: PekerjaCreate):
    eksekusi_tugas = PekerjaService(session)
    return eksekusi_tugas.tambah_pekerja(form=form)

@router.get("/", response_model=List[PekerjaRead], status_code=status.HTTP_200_OK)
def data_pekerja(session: SessionDep, offset: int=0, limit: int=10, search: str | None =None):
    eksekusi_tugas = PekerjaService(session)
    return eksekusi_tugas.get(
        limit=limit,
        offset=offset,
        search=search
    )

@router.patch("/{id_pekerja}", response_model=PekerjaUpdate, status_code=status.HTTP_200_OK)
def update_pekerja( session: SessionDep, id_pekerja: uuid.UUID,form: PekerjaUpdate):
    eksekusi_tugas = PekerjaService(session)
    return eksekusi_tugas.update_pekerja(id_pekerja, form)

@router.delete("/{id_pekerja}", status_code=status.HTTP_200_OK)
def delete_pekerja(session: SessionDep, id_pekerja: uuid.UUID):
    eksekusi_tugas = PekerjaService(session)
    return eksekusi_tugas.delete_pekerja(id_pekerja)



scan_only = APIRouter(prefix='/scan', tags=['scan'], dependencies=[Depends(verifikasi_perangkat)])
#untuk scan rfid dari esp supaya muncul uid nya di frontend
@scan_only.post("/", status_code=status.HTTP_200_OK)
def scan_rfid(form: RFIDScan):
    try:
        return {
            "status": "SUCCESS",
            "message": "UID RFID BERHASIL DITERIMA",
            "rfid_uid": form.uid_rfid
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GAGAL MENANGKAP UID: {str(e)}"
        )



