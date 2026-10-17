# raw_path, raw_size = simpan_foto(image_bytes, str(log.id), "raw")
from pathlib import Path

def simpan_foto(data: bytes, log_id: str) -> tuple[str, int]:
    path = Path("logs/raw") / f"{log_id}.jpg"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return str(path), len(data)