from datetime import datetime
from sqlmodel import Field, SQLModel
import uuid

class PekerjaBase(SQLModel):
  """DATA MODEL DASAR UNTUK DATA PEKERJA"""
  name: str
  rfid_uid: str
  role: str

class Pekerja(PekerjaBase, table=True):
  """TABEL PEKERJA"""
  __tablename__ = 'pekerja'
  id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
  name: str = Field(index=True, unique=True)
  rfid_uid: str = Field(index=True, unique=True) 
  created_at: datetime = Field(default_factory=datetime.now)
  is_active: bool = Field(default=True)

class PekerjaCreate(PekerjaBase):
  """DATA REQUEST DARI CLIENT UNTUK CREATE DATA"""
  pass

class PekerjaUpdate(SQLModel): 
  """DATA REQUEST DARI CLIENT UNTUK UPDATE DATA"""

  name: str | None = None 
  rfid_uid: str | None = None
  role: str | None = None
  is_active: bool | None = None


class PekerjaRead(PekerjaBase):
  """DATA RESPONSE"""
  id: uuid.UUID
  is_active: bool
  created_at: datetime

class RFIDScan(SQLModel):
  """DATA MODEL KARTU RFID"""
  uid_rfid: str