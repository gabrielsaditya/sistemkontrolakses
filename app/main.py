from fastapi import Depends,FastAPI, APIRouter, HTTPException, status
import models
from routers.pekerja import router_pekerja

def create_app():
    app = FastAPI()
    app.include_router(router_pekerja)

app = FastAPI(
    title="Backend PPE Detection + RFID",
    version="1.0.0",
    description="backend untuk sistem deteksi gatekeeper PPE + RFID",
)
app.include_router(router_pekerja, prefix="/api/v1", tags=["pekerja"])

@app.get("/")
def index():
    return {"message":"sistem backend berjalan dengan baik"}



