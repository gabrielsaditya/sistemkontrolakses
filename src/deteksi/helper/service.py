import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

STORAGE_DIR = Path(os.getenv("ALAMAT_STORAGE"))

from ultralytics import YOLO
from huggingface_hub import hf_hub_download
import cv2
import numpy as np
from typing import List
from ..model import UploadFile

class Inference:
    def __init__(self, model = None):
        self.model: YOLO | None = None
        self.konfigurasi_deteksi_gambar = {
            'IMAGE_SIZE': 640,
            'IOU': 0.45,
            'DEVICE': 'cpu',
            'CONF': 0.5,
            'CLASSES': [0, 1],
            'CLASS_CONF': []
        }

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

    def atur_konfigurasi_deteksi_gambar(
            self,
            image_size: int = 640,
            iou: float = 0.45,
            device: str = 'cpu',
            half: bool = False,
            conf: float = 0.5,
            classes: list = None,
            class_conf: dict = {},
        ):
        #MENDUKUNG PERUBAHAN PARSIAL
        self.konfigurasi_deteksi_gambar['IMAGE_SIZE'] = image_size
        self.konfigurasi_deteksi_gambar['IOU'] = iou
        self.konfigurasi_deteksi_gambar['DEVICE'] = device
        self.konfigurasi_deteksi_gambar['HALF'] = half
        self.konfigurasi_deteksi_gambar['CONF'] = conf
        self.konfigurasi_deteksi_gambar['CLASSES'] = classes
        self.konfigurasi_deteksi_gambar['CLASSES_CONF'] = class_conf

        print(f"BERHASIL SET CONFIG")
        return self.konfigurasi_deteksi_gambar  

        #MENDUKUNG PERUBAHAN PARSIAL YHEUU
    def parsing_class_yang_dapat_dideteksi(self):
        if not self.model:
            return {}
        return self.model.names
    
    async def prediksi_gambar(self, images: list[UploadFile], alamat_raw: Path, alamat_terdeteksi: Path) -> List[dict]:

        #1.OLAH DATA BYTES DARI ESP JADI ARRAY NUMPY YANG BISA DI PASSING KE YOLO, CONVERT DULU KE RGB
        if self.model is None:
            raise RuntimeError('MODEL BELUM DI LOAD... LOAD DULU!')

        if not images:
            raise ValueError("GAMBAR TIDAK BOLEH KOSONG BRO")
        
        alamat_raw.mkdir(parents=True, exist_ok=True)
        alamat_terdeteksi.mkdir(parents=True, exist_ok=True)

        image_source = []
        path_raw = []

        for index, image in enumerate(images):
            nama_file = image.filename
            image = await image.read()
            array = np.frombuffer(image, np.uint8)
            frame = cv2.imdecode(array, cv2.IMREAD_COLOR)

            if frame is None:
                raise ValueError(f"GAMBAR TIDAK VALID: {nama_file}")
            nama_raw = alamat_raw / f"{index}.jpg"
            if not cv2.imwrite(str(nama_raw), frame):
                raise RuntimeError(f"GAGAL MENYIMPAN GAMBAR: {nama_raw}")
            image_source.append(frame)
            path_raw.append(str(nama_raw))

        konfigurasi =  self.konfigurasi_deteksi_gambar
        hasil_deteksi_semua_gambar = []
        try:
        #2. JALANKAN PREDIKSI 
            results = self.model.predict(
                source=image_source,
                conf=konfigurasi['CONF'],
                iou=konfigurasi['IOU'],
                imgsz=konfigurasi['IMAGE_SIZE'],
                classes=konfigurasi['CLASSES'] or None,
                device=konfigurasi['DEVICE'],
                verbose=False,
            )
            #3. ITERASI PER GAMBAR -> PROSES PER GAMBAR YA
            for result in results:
                nama_gambar_terdeteksi = alamat_terdeteksi / f"{index}.jpg"

                if not cv2.imwrite(str(nama_gambar_terdeteksi), result.plot()):
                    raise RuntimeError(f"GAGAL MENYIMPAN: {nama_gambar_terdeteksi}")

                boxes = result.boxes
                #SEBAGAI CATATAN RESULT INI OBJECT BUKAN DICTIONARY
                list_bounding_box = result.boxes.xyxy.tolist()
                list_kelas_terdeteksi = result.boxes.cls.int().tolist()
                list_confidence = result.boxes.conf.tolist()

                if not (len(list_bounding_box) == len(list_kelas_terdeteksi) == len(list_confidence)):
                    raise ValueError('PANJANG LIST TIDAK SESUAI')

                hasil_deteksi_semua_gambar.append(
                    {
                    'LIST_BOUNDING_BOX' : list_bounding_box,
                    'LIST_KELAS_TERDETEKSI' : list_kelas_terdeteksi,
                    'CONF_LIST' : list_confidence,
                    "PATH_RAW": path_raw[index],
                    "PATH_ANNOTATED": str(nama_gambar_terdeteksi),
                    }
                )
                #DIAMBIL MASING MASING DI SATU GAMBARNYA
            return hasil_deteksi_semua_gambar[0] if len(hasil_deteksi_semua_gambar) == 1 else hasil_deteksi_semua_gambar                
        except Exception as e:
            raise RuntimeError(f"TERJADI KESALAHAN SAAT MELAKUKAN INFERENSI: {e}")


_inference: Inference | None = None

def get_inference() -> Inference:
    #DIGUNAKAN KETIKA DI FILE MAIN.PY SUPAYA MODEL DI LOAD SEKALI SAAT SERVER BACKEND DIJALANKAN
    global _inference
    if _inference is None:
        _inference = Inference()
    return _inference



