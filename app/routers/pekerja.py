from fastapi import APIRouter, HTTPException, status
from sqlmodel import select, or_
from typing import List
import uuid
from db import SessionDep
from models import (
    Pekerja,
    PekerjaCreate,
    PekerjaRead,
    PekerjaUpdate,
    RFIDScan
)
from pydantic import ValidationError

router_pekerja = APIRouter(prefix="/pekerja", tags=['pekerja'])

@router_pekerja.post("/", response_model=PekerjaRead, status_code=status.HTTP_201_CREATED)
def create_pekerja(pekerja_in: PekerjaCreate, session: SessionDep):
    existing = session.exec(select(Pekerja).where(Pekerja.rfid_uid == pekerja_in.rfid_uid)).first()
    if existing:
        raise HTTPException(status_code=400, detail="PEKERJA SUDAH TERDAFTAR")

    try:
        db_pekerja = Pekerja.model_validate(pekerja_in)
        session.add(db_pekerja)
        session.commit()
        session.refresh(db_pekerja)
        return db_pekerja
    
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"FORMAT DATA TIDA VALID: {str(e)}"
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GAGAL MENYIMPAN KE DATABASE: {str(e)}"
        )

@router_pekerja.get("/", response_model=List[PekerjaRead], status_code=status.HTTP_200_OK)
def read_pekerja(offset: int=0, limit: int=10, search: str | None = None, session: SessionDep = None):
    try:
        statement = select(Pekerja)
        if search:
            statement = statement.where(or_(Pekerja.name.ilike(f"%{search}%"), Pekerja.rfid_uid.ilike(f"%{search}%")))

        statement = statement.offset(offset).limit(limit)
        pekerja_list = session.exec(statement).all()
        return pekerja_list

    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GAGAL MENGAMBIL DATA PEKERJA: {e}"
        )
    
@router_pekerja.put("/{pekerja_id}", response_model=PekerjaRead, status_code=status.HTTP_200_OK)
def update_pekerja(payload: PekerjaUpdate, pekerja_id: uuid.UUID,session: SessionDep = None):
    try:
        pekerja = session.get(Pekerja, pekerja_id)
        if not pekerja:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, details='f"PEKERJA TIDAK DITEMUKAN')
        pekerja_data =  payload.model_dump(exclude_unset=True)
        for key, value in pekerja_data.items():
            setattr(pekerja, key, value)

        session.add(pekerja)
        session.commit()
        session.refresh(pekerja)

        return pekerja
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'GAGAL UPDATE DATA PEKERJA: {e}'
        )

@router_pekerja.delete("/{pekerja_id}", response_model=PekerjaRead, status_code=status.HTTP_200_OK)
def delete_pekerja(pekerja_id: uuid.UUID, session: SessionDep = None):
    try:
        pekerja = session.get(Pekerja, pekerja_id)
        if not pekerja:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, details=f"PEKERJA TIDAK DITEMUKAN")
        session.delete(pekerja)
        session.commit()
        session.refresh(pekerja)
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=f"GAGAL MENGHAPUS DATA PEKERJA: {e}"
        )

@router_pekerja.post("/scan-rfid", status_code=status.HTTP_200_OK)
def scan_rfid(payload: RFIDScan):
    try:
        return {
            "status": "SUCCESS",
            "message": "UID RFID BERHASIL DITERIMA",
            "rfid_uid": payload.rfid_uid
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GAGAL MENANGKAP UID: {str(e)}"
        )



    