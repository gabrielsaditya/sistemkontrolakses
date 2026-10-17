from fastapi import Depends,FastAPI, APIRouter, HTTPException, status
from app.pekerja.routes import router_pekerja
from app.deteksi.routes import router_deteksi
from app.db import create_db_and_tables, drop_tables
from contextlib import asynccontextmanager
from app.deteksi.helper_deteksi import Inference, get_inference
from huggingface_hub import hf_hub_download
from pathlib import Path

@asynccontextmanager
async def lifespan_model_inferensi(app: FastAPI):
    create_db_and_tables()
    get_inference().load_model_dari_huggingface(
        repo_id="leeyunjai/yolo11-ppe", 
        filename="ppe-11x.pt"
        )
    yield

app = FastAPI(
    title="Backend PPE Detection + RFID",
    version="1.0.0",
    description="backend untuk sistem deteksi gatekeeper PPE + RFID",
    lifespan=lifespan_model_inferensi
)

app.include_router(router=router_pekerja)
app.include_router(router=router_deteksi)


@app.get("/")
def index():
    return {"message":"sistem backend berjalan dengan baik wow"}



