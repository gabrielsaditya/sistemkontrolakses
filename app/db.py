import os
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv
from typing import Annotated
from fastapi import Depends

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"), echo=True)

def drop_tables():
    print("MENGHAPUSSS... TABEL DAN DATABASE")
    SQLModel.metadata.drop_all(engine)

def create_db_and_tables():
    print("MEMBUATZZZ TABEL DAN DATABASE...")
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        print("MEMBUATHH SESI BARU KONEKSI DATABASE...")
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
