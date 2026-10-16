from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form
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
from app.log_akses.models import LogAkses
from app.log_akses.log_servis import simpan_log
from pydantic import ValidationError
from datetime import datetime, timezone
from app.pekerja.models import Pekerja
from app.deteksi.helper_deteksi import get_inference
from app.deteksi import simpan_foto
import time

router_deteksi_gambar = APIRouter(prefix="/deteksi", tags=['deteksi'])

@router_deteksi_gambar.post('/predict', response_model=DeteksiResponse, status_code=status.HTTP_200_OK)
async def deteksi_gambar(
    session: SessionDep,
    images: List[UploadFile] = File(...),
    payload: DeteksiRequest = Depends()
):  
    #1. CEK PEKERJA
    t0 = payload.timestamp_dari_esp
    t1 = time.time() * 1000
    pekerja = session.exec(select(Pekerja).where(Pekerja.rfid_uid == payload.uid_rfid).first()
    if not pekerja:
        raise HTTPException(status_code=404, detail="PEKERJA TIDAK DITEMUKAN")

    #2. BACA FOTO YANG DIUPLOAD DARI ESP
    list_snapshot = []
    for image in images:
        list_snapshot.append(await image.read())
    t2 = time.time() * 1000 

    #3. INFERENSI
    model_deteksi = get_inference()
    jumlah_kelas_yang_dapat_dideteksi = len(model_deteksi.config['CLASSES'])
    try:
        semua_hasil_inferensi = model_deteksi.prediksi_gambar(list_snapshot)
    except Exception as e:
        raise HTTPException(500, f'GAGAL MELAKUKAN INFERENSI')
        votes_min = 2
        sucess_frame = 0

        for hasil in semua_hasil_inferensi:
            if len(hasil['LIST_KELAS_TERDETEKSI']) != jumlah_kelas_yang_dapat_dideteksi:
                continue
            sucess_frame += 1

        if sucess_frame >= votes_min:

            log = LogAkses(
                pekerja_id=pekerja.id,
                pekerja_nama=pekerja.nama,
                rfid_uid=payload.uid_rfid,

                keputusan=keputusan,          
                alasan=alasan,                

                detections=semua_hasil_inferensi,  

                foto_raw_path=,
                foto_annotated_path=foto_annotated_path,

                ukuran_foto_raw=ukuran_foto_raw,
                ukuran_foto_annotated=ukuran_foto_annotated,
                ukuran_foto_total=ukuran_foto_raw + ukuran_foto_annotated,

                latensi_1=t1-t0,
                latensi_2=t2-t1,
                latensi_3=t3-t2,
                latensi_4=t4-t2,
                latensi_total=latensi_1 + latensi_2 + latensi + 3 + latensi_4,
            )
            session.add(log)
            session.commit()
            session.refresh(log)
            }

            return DeteksiResponse(
                keputusan=True,
                alasan="APD LENGKAP",
                nama_pekerja=pekerja.nama,
                timestamp=datetime.now().isoformat()
            )
        else:
            return DeteksiResponse {
                keputusan=False,
                alasan='APD TIDAK LENGKAP',
                nama_pekerja=pekerja.nama,
                timestamp=datetime.now().isoformat()
            }

    except Exception as e:
        raise HTTPException(500, f'GAGAL MELAKUKAN INFERENSI GAMBAR: {e}')



@router_deteksi_gambar.post("/predict", response_model=LogAksesResponse, status_code=status.HTTP_200_OK)
async def deteksi_inferensi(
    session: SessionDep,
    image: UploadFile = File(...),
    payload: DeteksiRequest = Depends(),
):
    image_bytes = await image.read()        

    model_deteksi = get_inference()         
    model_deteksi.set_config(
        image_size=640, iou=0.45, conf=0.5, device="cpu",
    )

    try:
        hasil_inferensi = model_deteksi.predict_image(image_bytes)
        rangkuman = model_deteksi.get_summary_frame(hasil_inferensi)
    except Exception as e:
        raise HTTPException(500, f"GAGAL MELAKUKAN DETEKSI: {e}")

    kelas_terdeteksi = {d["name"] for d in rangkuman["detections"]}
    apd_wajib = {"helmet", "vest"}        

    keputusan = apd_wajib.issubset(kelas_terdeteksi)
    if keputusan:
        alasan = None
    else:
        kurang = apd_wajib - kelas_terdeteksi
        alasan = f"TIDAK LENGKAP: {', '.join(kurang)}"

    log = LogAkses(
        rfid_uid=payload.uid_rfid,
        keputusan=keputusan,
        alasan=alasan,
        detections=rangkuman["detections"],
        latensi_3=rangkuman["kecepatan_inferensi"],
    )
    session.add(log)
    session.commit()
    session.refresh(log)

    raw_path, raw_size = simpan_foto(image_bytes, str(log.id), "raw")
    log.foto_raw_path = raw_path
    log.ukuran_foto_raw = raw_size
    session.add(log)
    session.commit()
    session.refresh(log)

    return log

@router_deteksi_gambar.get(path="/konfigurasi",response_model=Konfigurasi, status_code=status.HTTP_200_OK)
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
    
@router_deteksi_gambar.patch("/konfigurasi", response_model=Konfigurasi)
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