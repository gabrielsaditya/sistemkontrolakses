from ultralytics import YOLO
from huggingface_hub import hf_hub_download
from typing import Optional

class Inference:
    def __init__(self, model_path: str = 'best.pt', conf: float=0.5):
        self.model_path = model_path
        self.conf = conf
        self.model: Optional[YOLO] = None
        self.config = {}

        self.init_model()

    def init_model(self):
        try:
            self.model= YOLO(self.model_path)
        except Exception as e:
            print(f"GAGAL LOAD MODEL!, ERROR: {e}")

    def set_config(
            self,
            image_size: int = 640,
            iou: float = 0.45,
            device: str = 'cpu',
            half: bool = False,
            conf: float = 0.5,
            classes: list = None,
            class_conf: dict = {
                None
            },
        ):
        self.config = {
            'image_size': image_size,
            'iou': iou,
            'device': device,
            'half': half,
            'conf': conf,
            'classes': classes if classes is Not None else [],  
            'class_conf': class_conf if class_conf is not None else {}
        }
        return self.config  

    def parsing_class(self):
        if not self.model:
            return {}
        return self.model.names

