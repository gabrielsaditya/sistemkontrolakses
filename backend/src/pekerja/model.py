import uuid

from datetime import datetime, timezone
from sqlmodel import Field, SQLModel
from pydantic import BaseModel

class PekerjaCreate(BaseModel):
  """DATA REQUEST DARI CLIENT UNTUK CREATE DATA"""
  name: str
  rfid_uid: str
  role: str 
  created_at: datetime
  is_active: bool = Field(default_factory= True)

class PekerjaUpdate(BaseModel): 
  """DATA REQUEST DARI CLIENT UNTUK UPDATE DATA"""

  name: str | None = None 
  rfid_uid: str | None = None
  role: str | None = None
  is_active: bool | None = None

class PekerjaRead(BaseModel):
  """DATA RESPONSE"""
  id: uuid.UUID 
  name: str 
  rfid_uid: str 
  role: str
  is_active: bool 
  
class RFIDScan(BaseModel):
  """DATA MODEL KARTU RFID"""
  uid_rfid: str
