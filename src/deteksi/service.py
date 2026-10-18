import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

STORAGE_DIR = Path(os.getenv("ALAMAT_STORAGE"))

if not STORAGE_DIR.is_absolute():
    STORAGE_DIR = BASE_DIR / STORAGE_DIR

from .model import DeteksiRequest, DeteksiResponse
from ..core.db import SessionDep
from ..entities.pekerja import Pekerja
from ..entities.log_akses import TabelLogAkses
from ..entities.konfigurasi_deteksi import TabelKonfigurasiDeteksi
from .helper.service import get_inference
from .model import DeteksiRequest, Konfigurasi
import time
import uuid
from sqlmodel import Session, select
from fastapi import HTTPException
from datetime import datetime, timezone
from ..logging_config import logging
from dotenv import load_dotenv


class DeteksiService:
    def __init__(self, session: SessionDep):
        self.session = session
        self.inference = get_inference()

    async def deteksi_gambar(self, images, form: DeteksiRequest):
        #1. timestamp esp
        t0 = form.latensi_request
        log_id = uuid.uuid4()

        alamat_foto_raw = storage_dir / "raw" / f"{log_id}.jpg"
        alamat_foto_after_deteksi = storage_dir / "annotated" / f"{log_id}.jpg"
        try:
            pekerja = self.session.exec(select(Pekerja).where(Pekerja.rfid_uid == form.uid_rfid)).first()
            if not pekerja:
                raise HTTPException(404, 'PEKERJA TIDAK DITEMUKAN')

            #2. t1 - t0 = latensi udara dari esp sampai ke server
            t1 = time.perf_counter() 
            hasil = await self.inference.prediksi_gambar(images)
            hasil_per_gambar = hasil if isinstance(hasil, list) else [hasil]

            #3. t2-t1 = latensi inferensi batch gambar
            t2 = time.perf_counter()
            keputusan_per_gambar = []
            semua_item = []


            for hasil_gambar in hasil_per_gambar:
                kelas = hasil_gambar["LIST_KELAS_TERDETEKSI"]
                nama_kelas = [
                    self.inference.model.names[k]
                    for k in set(kelas)
                ]
                semua_item.extend(nama_kelas)

            
                apd_lengkap = 0 in kelas and 2 in kelas
                keputusan_per_gambar.append(apd_lengkap)

            jumlah_diterima = sum(keputusan_per_gambar)
            keputusan_akhir = (
                True
                if jumlah_diterima > len(keputusan_per_gambar) / 2
                else False
            )
            timestamp_akses = datetime.now(timezone.utc)

            log = TabelLogAkses(
                id_pekerja=pekerja.id,
                uid_rfid=pekerja.rfid_uid,
                nama_pekerja=pekerja.name,
                latensi_udara_masuk = t1 - t0,
                latensi_inferensi = t2-t1,
                latensi_total = t2 -t0,
                item_terdeteksi=list(set(semua_item)),
                keputusan=keputusan_akhir,
                tanggal_akses=timestamp_akses
            )

            self.session.add(log)
            self.session.commit()
            self.session.refresh(log)



            #3. latensi proses parsing hasil keputusan dan tambah log ke db
            return {
                "keputusan_akses": keputusan_akhir,
                "nama_pekerja": pekerja.name,
                'uid_rfid': pekerja.rfid_uid
            }
        except Exception as e:
            self.session.rollback()
            logging.exception("GAGAL DETEKSI GAMBAR")
            raise HTTPException(500, 'Internal Server Error') from e


    #konfigurasi
    def update_konfigurasi(self, payload: Konfigurasi): 
        logging.info(f"1. MULAI QUERY")   
        try:
            statement = select(TabelKonfigurasiDeteksi)
            konfigurasi = self.session.exec(statement).first()
            if not konfigurasi:
                raise HTTPException(404, 'TIDAK DITEMUKAN KONFIGURASI')
            for key, value in payload.model_dump(exclude_unset=True).items():
                setattr(konfigurasi, key, value)
            self.session.add(konfigurasi)
            self.session.commit()
            self.session.refresh(konfigurasi)
            return konfigurasi
        except HTTPException:
            raise        
        
        except Exception as e:
            raise HTTPException(500, 'INTERNAL SERVER ERROR')

    def lihat_konfigurasi(self):
        logging.info("1. MULAI QUERY")
        try:
            statement = select(TabelKonfigurasiDeteksi)
            logging.info("2. STATEMENT DIBUAT")

            result = self.session.exec(statement)
            logging.info("3. QUERY DIEKSEKUSI")

            konfigurasi = result.first()
            logging.info(f"4. HASIL DIAMBIL: {konfigurasi}")

            return konfigurasi

        except Exception as e:
            raise HTTPException(500, 'QUERY GAGAL')
            
