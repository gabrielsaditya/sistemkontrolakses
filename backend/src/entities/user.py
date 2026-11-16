from sqlmodel import SQLModel, Field
import uuid

class User(SQLModel, table=True):
    __tablename__ = "user"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(min_length=6, max_length=20, unique=True, index=True)
    hashed_password: str = Field(min_length=6)
    role: str = Field(default="user")
        