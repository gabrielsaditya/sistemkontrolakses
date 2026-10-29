from fastapi import APIRouter, status, Depends
from ..auth.dependency import SessionDep
from .model import ReadLog, UpdateLog, CreateLog
from .service import LogAksesService
import uuid
from typing import List
from ..auth.dependency import require_role

router = APIRouter(prefix='/logs', tags=['logs'], dependencies=Depends([require_role('admin')]))

@router.post("/", response_model=ReadLog, status_code=status.HTTP_201_CREATED)
def create_logs(session: SessionDep, form: CreateLog):
    servis = LogAksesService(session)
    return servis.create_log(form)

@router.get("/", response_model=List[ReadLog], status_code=status.HTTP_200_OK)
def read_logs(session: SessionDep, offset: int=0, limit: int=10, search: str | None =None):
    servis = LogAksesService(session)
    return servis.read_log(
        limit=limit,
        offset=offset,
        search=search
    )

@router.patch("/{id_log}", response_model=ReadLog, status_code=status.HTTP_200_OK)
def edit_logs(session: SessionDep, id_log: uuid.UUID,form: UpdateLog):
    servis = LogAksesService(session)
    return servis.edit_log(id_log, form)

@router.delete("/{id_lod}", status_code=status.HTTP_200_OK)
def delete_log(session: SessionDep, id_log: uuid.UUID):
    servis = LogAksesService(session)
    return servis.delete_log(id_log)