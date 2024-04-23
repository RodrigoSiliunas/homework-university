from datetime import datetime
from sqlmodel import SQLModel, Field


class ValidToken(SQLModel, table=True):
    __tablename__ = "valid_tokens"

    id: int = Field(default=None, primary_key=True, unique=True)
    user_id: int = Field(unique=True, foreign_key="user.id")
    access_token_id: str
    access_expiration_date: datetime
    refresh_token_id: str
    refresh_expiration_date: datetime

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
