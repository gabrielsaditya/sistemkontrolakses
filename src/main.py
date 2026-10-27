from fastapi import FastAPI
from .core.db import create_db_and_tables, buat_konfigurasi_default
from .deteksi.service import get_inference
from .logging_config import LogLevel, konfigurasi_logging
from contextlib import asynccontextmanager
from .api import tambah_route

#1. KONFIGURASI LOGGING SUPAYA ERROR ATAU DEBUGGING BISA TER TRACE DENGAN BAIK
konfigurasi_logging(LogLevel.DEBUG)

#2. KASIH CONTENXT MANAGER SUPAYA MODEL DI LOAD DARI AWAL SERVER DIMULAI DAN NANTINYA PAKAI SESSION MODEL ITU TERUS TIDA LOAD BERKALI KALI
@asynccontextmanager
async def lifespan_model_inferensi(app: FastAPI):
    
    create_db_and_tables()
    buat_konfigurasi_default()
    get_inference().load_model_dari_huggingface(
        repo_id="leeyunjai/yolo11-ppe", 
        filename="ppe-11x.pt"
        )
    
    yield

#4. INISIALISASI SERVER BACKEND
app = FastAPI(
    title="BACKEND PPE DETECTION AND RFID",
    version="1.0.0",
    description="BACKEND UNTUK SISTEM KONTROL AKSES AREA BERBASIS IOT DAN COMPUTER VISION",
    lifespan=lifespan_model_inferensi
)

#5. TAMBAH ROUTE 
tambah_route(app)

#6. HOME ENDPOINT AJA
@app.get("/")
def index():
    return {"message":"sistem backend berjalan dengan baik wow"}



