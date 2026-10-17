from fastapi import APIRouter, HTTPException, status
from typing import List
import uuid
from src.core.db import SessionDep
from src.pekerja.model import (
    PekerjaCreate,
    PekerjaRead,
    PekerjaUpdate,
    PekerjaDelete,
    RFIDScan
)
from ..entities.pekerja import Pekerja
from src.pekerja.service import PekerjaService

router = APIRouter(prefix="/pekerja", tags=['pekerja'])

@router.post("/", response_model=PekerjaRead, status_code=status.HTTP_201_CREATED)
def tambah_pekerja(form: PekerjaCreate, session: SessionDep):
    eksekusi_tugas = PekerjaService(session)
    return eksekusi_tugas.tambah_pekerja(form=form)

@router.get("/", response_model=List[PekerjaRead], status_code=status.HTTP_200_OK)
def data_pekerja(offset: int=0, limit: int=10, search: str | None =None, session=SessionDep):
    eksekusi_tugas = PekerjaService(session)
    return eksekusi_tugas.get(
        limit=limit,
        offset=offset,
        search=search
    )

@router.patch("/", response_model=PekerjaUpdate, status_code=status.HTTP_200_OK)
def update_pekerja(form: PekerjaUpdate, session: SessionDep):
    eksekusi_tugas = PekerjaService(session)
    return eksekusi_tugas.update_pekerja(form)

@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_pekerja(id: uuid.UUID, session: SessionDep):
    eksekusi_tugas = PekerjaService(session)
    return eksekusi_tugas.delete_pekerja(id)

@router.post("/scan-rfid", status_code=status.HTTP_200_OK)
def scan_rfid(form: RFIDScan):
    try:
        return {
            "status": "SUCCESS",
            "message": "UID RFID BERHASIL DITERIMA",
            "rfid_uid": form.rfid_uid
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GAGAL MENANGKAP UID: {str(e)}"
        )



