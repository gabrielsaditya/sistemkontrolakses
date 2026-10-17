from fastapi import FastAPI
from src.pekerja.controller import router as router_pekerja

def tambah_route(app: FastAPI):
    app.include_router(router=router_pekerja)
