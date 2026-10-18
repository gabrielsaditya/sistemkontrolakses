import uuid
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from sqlalchemy import or_
from .model import (
    PekerjaRead,
    PekerjaCreate,
    PekerjaUpdate,
    PekerjaDelete,
    RFIDScan
)
from ..entities.pekerja import Pekerja

class PekerjaService:
    def __init__(self, session: Session):
        self.session = session

    def get(
        self,
        limit: int = 10,
        offset: int = 0,
        search: str | None = None
    ) -> list[Pekerja]:
        statement = select(Pekerja)

        if search:
            statement = statement.where(
                or_(
                    Pekerja.name.ilike(f"%{search}%"),
                    Pekerja.rfid_uid.ilike(f"%{search}%")
                )
            )

        statement = statement.offset(offset).limit(limit)

        try:
            return self.session.exec(statement).all()
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="GAGAL MENDAPATKAN DATA PEKERJA"
            )

    def get_by_id(self, id_pekerja: uuid.UUID) -> Pekerja:
        try:
            pekerja = self.session.get(Pekerja, id_pekerja)
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="GAGAL MENDAPATKAN DATA PEKERJA"
            )

        if pekerja is None:
            raise HTTPException(
                status_code=404,
                detail="PEKERJA TIDAK DITEMUKAN"
            )

        return pekerja

    def get_by_rfid_uid(self, rfid_uid: str) -> Pekerja:
        try:
            statement = select(Pekerja).where(
                Pekerja.rfid_uid == rfid_uid
            )
            pekerja = self.session.exec(statement).first()
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="GAGAL MENDAPATKAN DATA PEKERJA"
            )

        if pekerja is None:
            raise HTTPException(
                status_code=404,
                detail="PEKERJA TIDAK DITEMUKAN"
            )

        return pekerja

    def tambah_pekerja(self, form: PekerjaCreate) -> Pekerja:
        try:
            statement = select(Pekerja).where(
                Pekerja.rfid_uid == form.rfid_uid
            )
            existing = self.session.exec(statement).first()

            if existing:
                raise HTTPException(
                    status_code=409,
                    detail="RFID SUDAH TERDAFTAR"
                )

            pekerja = Pekerja.model_validate(form)
            self.session.add(pekerja)
            self.session.commit()
            self.session.refresh(pekerja)
            return pekerja

        except HTTPException:
            raise
        except IntegrityError:
            self.session.rollback()
            raise HTTPException(
                status_code=409,
                detail="DATA BERTENTANGAN DENGAN DATA YANG SUDAH ADA"
            )
        except Exception:
            self.session.rollback()
            raise HTTPException(
                status_code=500,
                detail="GAGAL MENYIMPAN PEKERJA"
            )

    def update_pekerja(
        self,
        id_pekerja: uuid.UUID,
        form: PekerjaUpdate
    ) -> Pekerja:
        try:
            pekerja = self.get_by_id(id_pekerja)

            for key, value in form.model_dump(
                exclude_unset=True
            ).items():
                setattr(pekerja, key, value)

            self.session.commit()
            self.session.refresh(pekerja)
            return pekerja

        except IntegrityError:
            self.session.rollback()
            raise HTTPException(
                status_code=409,
                detail="DATA BERTENTANGAN DENGAN DATA YANG SUDAH ADA"
            )
        except Exception:
            self.session.rollback()
            raise HTTPException(
                status_code=500,
                detail="GAGAL MEMPERBARUI DATA PEKERJA"
            )

    def delete_pekerja(self, id_pekerja: uuid.UUID) -> None:
        pekerja = self.get_by_id(id_pekerja)

        try:
            self.session.delete(pekerja)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise HTTPException(
                status_code=500,
                detail="GAGAL MENGHAPUS DATA PEKERJA"
            )


