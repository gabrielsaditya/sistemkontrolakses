from ultralytics import YOLO
from huggingface_hub import hf_hub_download
from typing import Optional

'''
cara pakai:
inferensi =  Inference(model_path, conf)
inferensi.set_config(...) sesuai parameter di setting aja
prediksi = inferensi.predict_image() -> nanti dia udah essuai sama konfignya
hasil_prediksi = prediksi.get_summary() -> tadi hasil dari prediksi  aan diparsing hasilnya
'''

class Inference:
    def __init__(self):
        self.model: Optional[YOLO] = None
        self.config = {
            'image_size': 640,
            'iou': 0.45,
            'device': 'cpu',
            'half': False,
            'conf': 0.5,
            'classes': None,
            'class_conf': {}
        }

    def load_model_dari_huggingface(self, repo_id: str, filename: str = 'best.pt'):
        try:
            model_path = hf_hub_download(repo_id=repo_id, filename=filename)
            self.model= YOLO(model_path)
            print(f"BERHASIL UNDUH DAN LOAD MODEL DARI HUGGING FACE")
        except Exception as e:
            print(f"GAGAL LOAD MODEL!, ERROR: {e}")

    def load_model_from_local(self, model_path: str):
        try:
            self.model = YOLO(model_path)
            print(f"BERHASIL LOAD MODEL DARI LOKAL")
        except Exception as e:
            print(f'GAGAL LOAD MODEL DARI LOKAL: {e}')

    def set_config(
            self,
            image_size: int = 640,
            iou: float = 0.45,
            device: str = 'cpu',
            half: bool = False,
            conf: float = 0.5,
            classes: list = None,
            class_conf: dict = {},
        ):
        self.config = {
            'image_size': image_size,
            'iou': iou,
            'device': device,
            'half': half,
            'conf': conf,
            'classes': classes,  
            'class_conf': class_conf or {}
        }
        print(f"BERHASIL SET CONFIG")
        return self.config  

    def parsing_class(self):
        if not self.model:
            return {}
        return self.model.names
    
    def predict_image(self, image_source):
        konfigurasi =  self.config
        try:
            results = self.model.predict(
                source=image_source,
                conf=konfigurasi['conf'],
                iou=konfigurasi['iou'],
                imgsz=konfigurasi['image_size'],
                classes=konfigurasi['classes'],
                device=konfigurasi['device'],
                half=konfigurasi.get('half', False),
                verbose=False,
            )

            return results[0] if results else None
        except Exception as e:
            print(f"TERJADI KESALAHAN SAAT MELAKUKAN INFERENSI: {e}")
        return None

    def get_summary_frame(self, results):
        'Untuk parsing hasil  deteksi  -> hanya per frame ya, yang dimasukkan objek resultsnya ya dari method predict_image '
        if not results: return None
        try:
            speed = getattr(results,'speed', {})
            kecepatan_inferensi = speed.get('inference', 0.0)
        except Exception:
            kecepatan_inferensi = 0.0

        detections = []
        if results.boxes:
            for box in results.boxes:
                cls_id = int(box.cls[0].item())
                conf = float(box.conf[0].item())
                class_name = self.model.names.get(cls_id, 'item_tidak_diketahui')

                detections.append({'name': class_name, 'tingkat_confidence': round(conf, 2) })

        return {'detections': detections, 'kecepatan_inferensi': kecepatan_inferensi}

_inference: Inference | None = None

def get_inference() -> Inference:
    global _inference
    if _inference is None:
        _inference = Inference()
    return _inference