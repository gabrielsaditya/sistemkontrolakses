import os
from sqlmodel import SQLModel, select, create_engine, Session
from dotenv import load_dotenv
from typing import Annotated
from fastapi import Depends
from ..entities.konfigurasi_deteksi import TabelKonfigurasiDeteksi

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"), echo=True)

def buat_konfigurasi_default():
    with Session(engine) as session:
        konfigurasi = session.exec(
            select(TabelKonfigurasiDeteksi)
        ).first()

        if konfigurasi is None:
            session.add(TabelKonfigurasiDeteksi())
            session.commit()

def create_db_and_tables():
    print("MEMBUATZZZ TABEL DAN DATABASE...")
    SQLModel.metadata.create_all(engine)
    print(SQLModel.metadata.tables.keys())

def get_session():
    with Session(engine) as session:
        print("MEMBUATHH SESI BARU KONEKSI DATABASE...")
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
