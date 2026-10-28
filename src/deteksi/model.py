import uuid
import time
from typing import List, Annotated
from sqlmodel import SQLModel, Field
from datetime import datetime
from pydantic import WithJsonSchema
from fastapi import UploadFile as FastAPIUploaFileOriginal


UploadFile = Annotated[FastAPIUploaFileOriginal, WithJsonSchema({
    'type': 'string',
    'format': 'binary'
})]



#DTO - HTTP -> DATA REQUEST DAN RESPONSE
class Konfigurasi(SQLModel):
    id: uuid.UUID | None
    model_path: str | None
    image_size: int | None
    iou: float | None
    conf: float | None
    classes: List[int] | None
    minimum_vote_foto: int | None

class DeteksiRequest(SQLModel):
    device_id: str 
    uid_rfid: str 
    latensi_request: float = Field(default_factory=time.perf_counter)    

class DeteksiResponse(SQLModel):
    keputusan_akses: bool
    nama_pekerja: str
    uid_rfid: str


