import uuid
from typing import List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON

class TabelKonfigurasiDeteksi(SQLModel, table=True):
    __tablename__ = 'konfigurasi_deteksi'

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    id_user: uuid.UUID = Field(
    foreign_key="user.id",
    ondelete="RESTRICT"
    )
    model_path: str = "best.pt"
    image_size: int = 640
    iou: float = 0.45
    conf: float = 0.5
    classes: List[int] | None = Field(default=None, sa_column=Column(JSON))
    minimum_vote_foto: int = 1

    user: 'User' = Relationship(back_populates='konfigurasi_deteksi')