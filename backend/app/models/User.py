from enum import Enum
from datetime import datetime
from sqlmodel import SQLModel, Relationship, Field
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserType(str, Enum):
    normal = 'normal'
    administrator = 'administrator'


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True, unique=True)

    name: str
    username: str
    email: str = Field(unique=True)
    password: str
    last_login_at: datetime = Field(default_factory=datetime.utcnow)
    active: bool = False
    # Por padrão todos usuários são do tipo normal, ele vira um administrador quando for necessário, alterando o banco de dados.
    type: UserType = Field(default=UserType.normal) 


    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    tweet_list: list["UserTweet"] = Relationship(back_populates="user")

    def set_password(self, password: str):
        self.password = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password)
