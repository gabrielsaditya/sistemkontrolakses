from fastapi import FastAPI,status, APIRouter,Depends, HTTPException, Form, File, UploadFile as UF
from typing import Annotated
from .model import (DeteksiRequest, DeteksiResponse, Konfigurasi)
from .service import DeteksiService
from ..core.db import SessionDep
from datetime import datetime
from ..logging_config import logging
from pydantic import WithJsonSchema
from .model import UploadFile

router = APIRouter(prefix="/deteksi", tags=['deteksi'])

@router.post("/", response_model=DeteksiResponse, status_code=status.HTTP_200_OK)
async def deteksi_gambar(
    session: SessionDep, 
    images: list[UploadFile] = File(...), 
    device_id: str = Form(...),
    uid_rfid: str = Form(...)
):
    form = DeteksiRequest(
        device_id=device_id,
        uid_rfid=uid_rfid
    )
    servis = DeteksiService(session)
    return await servis.deteksi_gambar(images, form)

@router.get('/', response_model=Konfigurasi, status_code=status.HTTP_200_OK)
def lihat_konfigurasi(session: SessionDep):
    servis = DeteksiService(session)
    logging.info("WOWWWWWWWWWWWww")
    return servis.lihat_konfigurasi()

@router.patch("/", response_model=Konfigurasi, status_code=status.HTTP_200_OK)
def update_konfigurasi(session: SessionDep,form: Konfigurasi):
    servis = DeteksiService(session)
    return servis.update_konfigurasi(form)
