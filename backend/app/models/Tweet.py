from datetime import datetime
from typing import Optional
from pydantic import condecimal
from sqlmodel import SQLModel, Relationship, Field

class Tweet(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, unique=True)
    user_id: int = Field(foreign_key="user.id")

    text: str

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "text": self.text,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
