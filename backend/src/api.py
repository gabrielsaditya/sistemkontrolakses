from fastapi import FastAPI
from src.pekerja.controller import router as router_pekerja
from src.pekerja.controller import scan_only as router_scan
from src.pekerja.controller import scan_ws as router_scan_ws
from src.deteksi.controller import router as router_deteksi
from src.auth.controller import router as router_auth
from src.log_akses.controller import router as router_log
from src.perangkat_esp.monitoring_perangkat import router as router_monitoring_perangkat

"""
DISINI UNTUK INCLUDE ROUTER DARI MASING MASING FEATURE YANG ADA
"""

def tambah_route(app: FastAPI):
    app.include_router(router=router_pekerja)
    app.include_router(router=router_deteksi)
    app.include_router(router=router_auth)
    app.include_router(router=router_log)
    app.include_router(router=router_monitoring_perangkat)
    app.include_router(router=router_scan)
    app.include_router(router=router_scan_ws)