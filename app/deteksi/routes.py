from fastapi import APIRouter, HTTPException, status
from sqlmodel import select, or_
from typing import List
import uuid
from app.db import SessionDep
from app.deteksi.models import (
    TabelKonfigurasiDeteksi,
    Konfigurasi,
    DeteksiRequest,
    DeteksiResponse
)
from pydantic import ValidationError
from datetime import datetime, timezone

router_deteksi = APIRouter(prefix="/deteksi", tags=['deteksi'])

@router_deteksi.post(response_model=DeteksiResponse, status_code=status.HTTP_200_OK)
def deteksi_inferensi(payload: DeteksiRequest,session: SessionDep):
    try:
        uid_rfid = payload.uid_rfid
        timestamp_dari_esp = payload.timestamp_dari_esp
        timestamp_endpoint_menerima = datetime.now(timezone.utc)

    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'GAGAL MELAKUKAN DETEKSI: {e}'
        )

@router_deteksi.get(path="/konfigurasi",response_model=Konfigurasi, status_code=status.HTTP_200_OK)
def get_konfigurasi(session: SessionDep):
    try:
        konfigurasi =  session.exec(select(TabelKonfigurasiDeteksi)).first()
        if not konfigurasi:
            raise HTTPException(404, 'TIDAK DITEMUKAN')
        return konfigurasi
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GAGAL MENGAMBIL DATA KONFIGURASI: {e}"
        )
    
@router_deteksi.patch("/konfigurasi", response_model=Konfigurasi)
def update_konfigurasi(payload: Konfigurasi, session: SessionDep):
    konfigurasi = session.exec(select(TabelKonfigurasiDeteksi)).first()
    if not konfigurasi:
        raise HTTPException(404, 'TIDAK DITEMUKAN')

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(konfigurasi, key, value)

    session.add(konfigurasi)
    session.commit()
    session.refresh(konfigurasi)
    return konfigurasi