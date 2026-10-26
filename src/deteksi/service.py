import os
from pathlib import Path
from dotenv import load_dotenv
import os

#membuat alamat storage
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
from .helper.service import get_inference, Inference
from .model import DeteksiRequest, Konfigurasi
import time
import uuid
from sqlmodel import Session, select
from fastapi import HTTPException
from datetime import datetime, timezone
from ..logging_config import logging
from dotenv import load_dotenv
from ..helper.ukur_cpu_ram import ukur_performa
from ..entities.konfigurasi_deteksi import TabelKonfigurasiDeteksi


class DeteksiService:
    def __init__(self, session: SessionDep):
        self.session = session
        self.inference = get_inference()
        self.konfigurasi_user = self._load_tabel_konfigurasi()

    def _load_tabel_konfigurasi(self):
        try:
            tabel_konfigurasi = self.session.exec(select(TabelKonfigurasiDeteksi)).first()
            if not tabel_konfigurasi:
                raise HTTPException(404, 'TABEL KONFIGURASI TIDAK DITEMUKAN')

            dictionary_tabel = tabel_konfigurasi.model_dump(exclude={'id'})
            print(dictionary_tabel)
            return dictionary_tabel
        except HTTPException:
            self.session.rollback()
            raise
        except Exception as e:
            self.session.rollback()
            raise HTTPException(500, 'GAGAL LOAD TABEL KONFIGURASI')
    
    async def deteksi_gambar(self, images, form: DeteksiRequest):
        #1. timestamp esp
        t0 = form.latensi_request
        log_id = uuid.uuid4()
        
        alamat_foto_raw = STORAGE_DIR / "raw" / str(log_id)
        alamat_foto_after_deteksi = STORAGE_DIR / "annotated" / str(log_id)

        try:

            ukur = ukur_performa()
            pekerja = self.session.exec(select(Pekerja).where(Pekerja.rfid_uid == form.uid_rfid)).first()
            if not pekerja:
                raise HTTPException(404, 'PEKERJA TIDAK DITEMUKAN')

            #2. t1 - t0 = latensi udara dari esp sampai ke server
            t1 = time.perf_counter() 
            list_hasil = await self.inference.prediksi_gambar(images, alamat_foto_raw, alamat_foto_after_deteksi, self.konfigurasi_user)

            #3. t2-t1 = latensi inferensi batch gambar
            t2 = time.perf_counter()

            #logic untuk voting
            jumlah_diterima = sum(hasil['LOLOS'] for hasil in list_hasil if hasil['LOLOS'])
            minimum_vote = self.konfigurasi_user['minimum_vote_foto']
            keputusan_akhir = jumlah_diterima >= minimum_vote

            #berhentikan pengukuran cpu dan ram 
            pemakaian_cpu, pemakaian_ram = ukur()
            log = TabelLogAkses(
                id_pekerja=pekerja.id,
                uid_rfid=pekerja.rfid_uid,
                nama_pekerja=pekerja.name,
                item_terdeteksi=[hasil['LIST_KELAS_TERDETEKSI'] for hasil in list_hasil],
                path_gambar_raw=[hasil['PATH_RAW'] for hasil in list_hasil],
                path_gambar_terdeteksi=[hasil['PATH_ANNOTATED'] for hasil in list_hasil],
                size_foto_raw=[hasil['SIZE_FOTO_RAW'] for hasil in list_hasil],
                size_foto_terdeteksi=[hasil['SIZE_FOTO_TERDETEKSI'] for hasil in list_hasil],
                keputusan_akses=keputusan_akhir,
                latensi_request = t1-t0,
                latensi_inferensi_yolo = t2-t1,
                latensi_total = t2-t0,    
                pemakaian_cpu=pemakaian_cpu,
                pemakaian_ram=pemakaian_ram
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
        except HTTPException:
            self.session.rollback()
            raise
        
        except Exception as e:
            self.session.rollback()
            logging.exception("GAGAL DETEKSI GAMBAR")
            raise HTTPException(500, 'Internal Server Error') from e


    #konfigurasi
    def update_konfigurasi(self, form: Konfigurasi): 
        try:
            konfigurasi = self.session.exec(select(TabelKonfigurasiDeteksi)).first()
            if not konfigurasi:
                raise HTTPException(404, 'TIDAK DITEMUKAN KONFIGURASI')
            for key, value in form.model_dump(exclude_unset=True, exclude={'id'}).items():
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
        try:
            konfigurasi = self.session.exec(select(TabelKonfigurasiDeteksi)).first()
            return konfigurasi

        except Exception as e:
            raise HTTPException(500, 'QUERY GAGAL')
            
