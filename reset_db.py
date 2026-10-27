from sqlmodel import SQLModel

from src.core.db import engine
from src.entities.pekerja import Pekerja
from src.entities.log_akses import TabelLogAkses
from src.entities.konfigurasi_deteksi import TabelKonfigurasiDeteksi
from src.entities.user import User

SQLModel.metadata.drop_all(engine)
SQLModel.metadata.create_all(engine)

print("DATABASE BERHASIL DIBUAT ULANG SESUAI SKEMA DAN ENTITASNYA")