from fastapi import FastAPI
from src.pekerja.controller import router as router_pekerja
from src.deteksi.controller import router as router_deteksi
"""
DISINI UNTUK INCLUDE ROUTER DARI MASING MASING FEATURE YANG ADA
"""

def tambah_route(app: FastAPI):
    app.include_router(router=router_pekerja)
    app.include_router(router=router_deteksi)