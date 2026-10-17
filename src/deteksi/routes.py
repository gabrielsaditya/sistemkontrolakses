from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from sqlmodel import select, or_
from typing import List
import uuid
from app.core.db import SessionDep
from app.deteksi.models import (
    TabelKonfigurasiDeteksi,
    Konfigurasi,
    DeteksiRequest,
    DeteksiResponse
)
from app.log_akses.models import LogAkses
from pydantic import ValidationError
from datetime import datetime, timezone
from app.features.pekerja.models import Pekerja
from app.deteksi.helper_deteksi import get_inference
from app.deteksi import simpan_foto
import time
import numpy as np
import cv2

router_deteksi = APIRouter(prefix="/deteksi", tags=['deteksi'])

@router_deteksi.post('/predict', response_model=DeteksiResponse, status_code=status.HTTP_200_OK)
async def deteksi_gambar(
    session: SessionDep,
    images: List[UploadFile] = File(...),
    payload: DeteksiRequest = Form(...)
):
    t0 = payload.timestamp
    t1 = time.time() * 1000
    latensi_udara = t1 - t0

    #1. cek dulu pekerja ada gak 
    pekerja = session.exec(select(Pekerja).where(Pekerja.rfid_uid == payload.uid_rfid)).first()
    if not pekerja:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PEKERJA TIDAK DITEMUKAN")

    #2. open image
    model_deteksi = get_inference()
    try:
        hasil_deteksi = model_deteksi.prediksi_gambar(images)        
        print(hasil_deteksi)
    except Exception as e:
        raise HTTPException(500, 'INFERENSI TIDAK DAPAT DILAKUKAN')


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