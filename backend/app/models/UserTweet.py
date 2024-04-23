from datetime import datetime
from sqlmodel import SQLModel, Relationship, Field
from typing import Optional

from app.models import (
    User,
    Tweet
)


class UserTweet(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, unique=True)

    user_id: int = Field(foreign_key="user.id")
    tweet_id: int = Field(foreign_key="tweet.id")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional[User] = Relationship(back_populates="tweet_list")