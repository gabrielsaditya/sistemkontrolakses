from fastapi import FastAPI, Request, status
from .core.db import create_db_and_tables, buat_konfigurasi_default
from .deteksi.service import get_inference
from .logging_config import LogLevel, konfigurasi_logging
from contextlib import asynccontextmanager
from .api import tambah_route
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # exc.errors() berisi daftar field yang error dan alasannya
    custom_errors = []
    for error in exc.errors():
        custom_errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"] if loc != "body"),
            "message": error["msg"],
            "type": error["type"]
        })
        
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "status": "fail",
            "message": "Validasi data gagal, bro!",
            "errors": custom_errors
        }
    )
#6. HOME ENDPOINT AJA
@app.get("/")
def index():
    return {"message":"sistem backend berjalan dengan baik wow"}



