from fastapi import Depends,FastAPI, APIRouter, HTTPException, status
from routers.pekerja import router_pekerja
from db import create_db_and_tables

create_db_and_tables()

app = FastAPI(
    title="Backend PPE Detection + RFID",
    version="1.0.0",
    description="backend untuk sistem deteksi gatekeeper PPE + RFID",
)
app.include_router(router=router_pekerja)


@app.get("/")
def index():
    return {"message":"sistem backend berjalan dengan baik"}



