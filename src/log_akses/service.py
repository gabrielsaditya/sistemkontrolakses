from ..entities.log_akses import TabelLogAkses
from ..entities.pekerja import Pekerja
from ..core.db import SessionDep
from sqlmodel import select, or_
from .model import CreateLog, ReadLog, UpdateLog
from fastapi import HTTPException
import uuid
from typing import List

class LogAksesService:
    def __init__(self, session: SessionDep):
        self.session = session

    def create_log(self, form: CreateLog):
        try:
            log = self.session.exec(select(TabelLogAkses).where(form.uid_rfid == form.uid_rfid))
            if log:
                raise HTTPException(404, 'LOG SUDAH ADA DI DATABASE')
            new_log = TabelLogAkses.model_validate(form)
            self.session.add(new_log)
            self.session.commit()
            self.session.refresh(new_log)
            return new_log
        except HTTPException:
            self.session.rollback()
            raise
        except Exception as e:
            self.session.rollback()
            raise HTTPException(500, 'GAGAL CREATE LOG')


    def read_log(self, limit: int, offset: int, id_pekerja: int | None = None, search: str | None = None) -> List[ReadLog]:
        try:
            statement = select(TabelLogAkses)

            if id_pekerja is not None:
                statement = statement.where(
                    TabelLogAkses.id_pekerja == id_pekerja
                )

            if search:
                statement = statement.where(
                    or_(
                        TabelLogAkses.nama_pekerja.ilike(f"%{search}%"),
                        TabelLogAkses.uid_rfid.ilike(f"%{search}%")
                    )
                )

            statement = statement.order_by(
                TabelLogAkses.tanggal_akses.desc(),
                TabelLogAkses.id.desc()
            )
            statement = statement.offset(offset).limit(limit)
            return self.session.exec(statement).all()
        except HTTPException:
            self.session.rollback()
            raise
        except Exception as e:
            self.session.rollback()
            raise HTTPException(500, 'GAGAL READ LOG DARI DATABASE')
        
    def edit_log(self, id_pekerja: uuid.UUID, form: UpdateLog):
        try:
            log = self.session.exec(TabelLogAkses.id == id_pekerja).first()
            if not log:
                raise HTTPException(404, 'LOG TIDAK DITEMUKAN')
            for key, value in form.model_dump(
                exclude_unset=True
            ).items():
                setattr(log, key, value)

            return log
        except HTTPException:
            self.session.rollback()
            raise
        except Exception as e:
            self.session.rollback()
            raise HTTPException(500, 'GAGAL MELAKUKAN EDIT LOG')
        
    def get_by_id(self, id_pekerja: uuid.UUID):
        try:
            log = self.session.get(TabelLogAkses.id, id_pekerja)
            if not log: 
                raise HTTPException(404, 'LOG TIDAK DITEMUKAN DENGAN ID TERKAIT')
            return log
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(500, 'GAGAL MENCARI LOG BY ID')
        
    def delete_log(self, id_pekerja: uuid.UUID):
        log = self.session.get_by_id(id_pekerja)
        try:
            self.session.delete(log)
            self.session.commit()
            self.session.refresh()
        except Exception as e:
            raise HTTPException(500, 'GAGAL MELAKUKAN DELETE LOG')