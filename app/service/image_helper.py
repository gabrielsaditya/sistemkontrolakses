from ultralytics import YOLO
from huggingface_hub import hf_hub_download
from app.service.detection_helper import Inference


# Download otomatis file model dari Hugging Face Hub
model_path = hf_hub_download(
    repo_id="melihuzunoglu/ppe-detection", 
    filename="best.pt"
)

class APDImageInference(Inference):
  
  def predict_image(self, image_source, config):
    iou = getattr(config, 'iou', 0.45)
    conf =  getattr(config, 'conf', 0.5)
    classes = getattr(config, 'classes', getattr(config, 'item', None))
    image_size = getattr(config, 'image_size', 640)
    device = getattr(config, 'device', 'cpu')

    global_conf = min(conf.values()) if isinstance(conf, dict) else conf
    try:
        results = self.model.predict(
            image_source, global_conf, iou, image_size, classes, device, verbose=False, half=device =='cpu'
        )

        return results[0] if results else None
    except Exception as e:
       print(f"TERJADI KESALAHAN SAAT MELAKUKAN INFERENSI: {e}")
       return None