import os
import cv2
import numpy as np
from ultralytics import YOLO
from huggingface_hub import hf_hub_download
from typing import List
from ..model import UploadFile
from pathlib import Path

class Inference:
    def __init__(self, model = None):
        self.model: YOLO | None = None

    def load_model_dari_huggingface(self, repo_id: str, filename: str = 'best.pt'):
        #HUGGING FACE ADALAH PLATFORM MODERN UNTUK UNDUH MODEL YANG SUDAH DILATIH BANYAK ORANG
        #SEHINGGA KITA TIDAK PERLU MELATIH MODEL DARI NOL LAGI, KARENA KITA KALAH DATASET DAN SPEK LOCAL PC HEHEHEHEHEHEHEHEHEEHHEHEHEHE WOWWWW
        try:
            model_path = hf_hub_download(repo_id=repo_id, filename=filename)
            self.model= YOLO(model_path)
            print(f"BERHASIL UNDUH DAN LOAD MODEL DARI HUGGING FACE")
            return self.model
        except Exception as e:
            print(f"GAGAL LOAD MODEL!, ERROR: {e}")

    def load_model_dari_lokal(self, model_path: str):
        try:
            self.model = YOLO(model_path)
            print(f"BERHASIL LOAD MODEL DARI LOKAL")
            return self.model
        except Exception as e:
            print(f'GAGAL LOAD MODEL DARI LOKAL: {e}')
    
    async def prediksi_gambar(self, images: list[UploadFile], alamat_raw: Path, alamat_terdeteksi: Path, konfigurasi) -> List[dict]:

        #1.OLAH DATA BYTES DARI ESP JADI ARRAY NUMPY YANG BISA DI PASSING KE YOLO, CONVERT DULU KE RGB
        if self.model is None:
            raise RuntimeError('MODEL BELUM DI LOAD... LOAD DULU!')

        if not images:
            raise ValueError("GAMBAR TIDAK BOLEH KOSONG BRO")
        
        alamat_raw.mkdir(parents=True, exist_ok=True)
        alamat_terdeteksi.mkdir(parents=True, exist_ok=True)
        image_source = []
        path_raw = []
        size_gambar_raw_mb = []

        for index, image in enumerate(images):
            nama_file = image.filename
            image = await image.read()
            array = np.frombuffer(image, np.uint8)
            frame = cv2.imdecode(array, cv2.IMREAD_COLOR)

            if frame is None:
                raise ValueError(f"GAMBAR TIDAK VALID: {nama_file}")
            
            nama_raw = alamat_raw / f"{index}_raw.jpg"
            if not cv2.imwrite(str(nama_raw), frame):
                raise RuntimeError(f"GAGAL MENYIMPAN GAMBAR: {nama_raw}")
            size_gambar_raw_mb.append(os.path.getsize(nama_raw) / (1024**2))
            image_source.append(frame)
            path_raw.append(str(nama_raw))

        hasil_deteksi_semua_gambar = []
        try:
        #2. JALANKAN PREDIKSI 
            results = self.model.predict(
                source=image_source,
                conf=konfigurasi['conf'] or 0.5,
                iou=konfigurasi['iou'] or 0.45,
                imgsz=konfigurasi['image_size'] or 640,
                classes=konfigurasi['classes'] or None,
                device='cpu',  # Catatan: 'device' tidak ada di tabel, bisa di-hardcode atau ditambah ke kolom tabel
                verbose=False,
            )
            #3. ITERASI PER GAMBAR -> PROSES PER GAMBAR YA
            for index, result in enumerate(results):
                nama_gambar_terdeteksi = alamat_terdeteksi / f"{index}_annotated.jpg"

                if not cv2.imwrite(str(nama_gambar_terdeteksi), result.plot()):
                    raise RuntimeError(f"GAGAL MENYIMPAN: {nama_gambar_terdeteksi}")
                size_gambar_terdeteksi_mb = os.path.getsize(nama_gambar_terdeteksi) / (1024**2)
                boxes = result.boxes
                #SEBAGAI CATATAN RESULT INI OBJECT BUKAN DICTIONARY
                list_bounding_box = result.boxes.xyxy.tolist()
                list_kelas_terdeteksi = result.boxes.cls.int().tolist()
                list_confidence = result.boxes.conf.tolist()
                keputusan_lolos = sorted(list_kelas_terdeteksi) == sorted(konfigurasi['classes'])

                if not (len(list_bounding_box) == len(list_kelas_terdeteksi) == len(list_confidence)):
                    raise ValueError('PANJANG LIST TIDAK SESUAI')

                hasil_deteksi_semua_gambar.append(
                    {
                    'LIST_BOUNDING_BOX' : list_bounding_box,
                    'LIST_KELAS_TERDETEKSI' : list_kelas_terdeteksi,
                    'CONF_LIST' : list_confidence,
                    "PATH_RAW": path_raw[index],
                    "PATH_ANNOTATED": str(nama_gambar_terdeteksi),
                    "SIZE_FOTO_RAW": float(size_gambar_raw_mb[index]),
                    "SIZE_FOTO_TERDETEKSI": float(size_gambar_terdeteksi_mb),
                    "LOLOS": keputusan_lolos
                    }
                )
            return hasil_deteksi_semua_gambar
        except Exception as e:
            raise RuntimeError(f"TERJADI KESALAHAN SAAT MELAKUKAN INFERENSI: {e}")

    async def inferensi_video(self, video_source):
        pass

_inference: Inference | None = None

def get_inference() -> Inference:
    #DIGUNAKAN KETIKA DI FILE MAIN.PY SUPAYA MODEL DI LOAD SEKALI SAAT SERVER BACKEND DIJALANKAN
    global _inference
    if _inference is None:
        _inference = Inference()
    return _inference


