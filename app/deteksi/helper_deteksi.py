from ultralytics import YOLO
from huggingface_hub import hf_hub_download
from typing import Optional
from io import BytesIO
from PIL import Image
import numpy as np
from pathlib import Path
import os

class Inference:
    def __init__(self, model = None):
        self.model: YOLO | None = None
        self.config = {
            'IMAGE_SIZE': 640,
            'IOU': 0.45,
            'DEVICE': 'cpu',
            'CONF': 0.5,
            'CLASSES': None,
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

    def atur_konfigurasi(
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
        self.config['IMAGE_SIZE'] = image_size
        self.config['IOU'] = iou
        self.config['DEVICE'] = device
        self.config['HALF'] = half
        self.config['CONF'] = conf
        self.config['CLASSES'] = classes
        self.config['CLASSES_CONF'] = class_conf

        print(f"BERHASIL SET CONFIG")
        return self.config  

    def parsing_class_yang_dapat_dideteksi(self):
        if not self.model:
            return {}
        return self.model.names

    def _bytes_ke_array(self, data: bytes) -> np.ndarray:
        '''
        METHOD KHUSUS UNTUK UBAH BYTES JPEG DARI ESP NANTI DIUBAH KE BENTUK JPEG YANG BISA DIDETEKSI YOLO
        '''
        return np.array(Image.open(BytesIO(data)).convert('RGB'))
    
    def prediksi_gambar(self, images):

        #1.OLAH DATA BYTES DARI ESP JADI ARRAY NUMPY YANG BISA DI PASSING KE YOLO, CONVERT DULU KE RGB
        if self.model is None:
            raise RuntimeError('MODEL BELUM DI LOAD... LOAD DULU!')

        if isinstance(images, (bytes, bytearray, np.ndarray)):
            images = [images]

        image_source = []
        for image in images:
            if isinstance(image,( bytes, bytearray)):
                image_source.append(self._bytes_ke_array(image))
            else:
                image_source.append(image)

        
        konfigurasi =  self.config
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
                save=True,
                project='uploads',
                name='predict',
                exist_ok=True
            )
            #3. ITERASI PER GAMBAR -> PROSES PER GAMBAR YA
            for result in results:
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
                    'CONF_LIST' : list_confidence
                    }
                )
                #DIAMBIL MASING MASING DI SATU GAMBARNYA
            return hasil_deteksi_semua_gambar[0] if len(hasil_deteksi_semua_gambar) == 1 else hasil_deteksi_semua_gambar                
        except Exception as e:
            raise RuntimeError(f"TERJADI KESALAHAN SAAT MELAKUKAN INFERENSI: {e}")

#FUNGSI UNTUK SIMPAN FOTO
def simpan_foto(data: bytes, log_id: str) -> tuple[str, int]:
    path = Path("logs/raw") / f"{log_id}.jpg"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return str(path), len(data)

_inference: Inference | None = None

def get_inference() -> Inference:
    #DIGUNAKAN KETIKA DI FILE MAIN.PY SUPAYA MODEL DI LOAD SEKALI SAAT SERVER BACKEND DIJALANKAN
    global _inference
    if _inference is None:
        _inference = Inference()
    return _inference
