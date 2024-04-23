from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Union

from fastapi import HTTPException, Header, Depends, status
from sqlalchemy.orm import Session

from app.configurations.database import engine
from app.models import User, UserType
from app.configurations.enviroments import (
    ENCRYPTION_ALGORITHM,
    SECRET_KEY,
    ACCESS_TOKEN_EXPIRES,
    REFRESH_TOKEN_EXPIRES
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_token(user: User, token_type: str) -> str:
    allowed_types = ["refresh", "access"]

    if token_type not in allowed_types:
        raise ValueError("Invalid token type")

    data = {
        "id": user.id,
        "name": user.name,
        "username": user.username,
        "email": user.email,
        "created_at": str(user.created_at),
        "updated_at": str(user.updated_at),
    }

    if token_type == "refresh":
        data["exp"] = datetime.utcnow() + timedelta(hours=REFRESH_TOKEN_EXPIRES)
    elif token_type == "access":
        data["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRES)

    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ENCRYPTION_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ENCRYPTION_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def decode_header_token(authorization: str = Header(...)) -> dict:
    token = authorization.replace("Bearer ", "")
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ENCRYPTION_ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def is_token_valid(expiration_date: datetime) -> bool:
    current_time = datetime.utcnow()
    return current_time < expiration_date


def get_user_by_id(db: Session, user_id: int) -> Union[User, None]:
    user_exists = db.query(User).filter(User.id == user_id).first()
    return user_exists

# Defina uma função para retornar uma nova sessão sempre que é chamada
def get_session() -> Session:
    with Session(engine) as session:
        yield session

# Agora você pode usar get_session() como uma dependência em vez de engine
def get_current_user(authorization: str = Depends(decode_header_token), db: Session = Depends(get_session)) -> User:
    user_id = authorization.get("id")
    user = get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(
            detail={
                "error": {
                    "message": "User does not exist",
                    "type": "UserError",
                    "code": 404
                }
            },
            status_code=404
        )

    return user



def is_user_administrator(user: User = Depends(get_current_user)) -> User:
    if user.type != UserType.administrator:
        raise HTTPException(
            detail={
                "error": {
                    "message": "Error. You don't have permission to perform this operation. You need to be an administrator.",
                    "type": "UserError",
                    "code": 403
                }
            },
            status_code=status.HTTP_403_FORBIDDEN
        )
    return user
