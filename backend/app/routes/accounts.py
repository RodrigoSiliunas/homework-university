from datetime import datetime, timedelta
from typing import Union

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.param_functions import Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.configurations.enviroments import (
    ACCESS_TOKEN_EXPIRES,
    REFRESH_TOKEN_EXPIRES
)
from app.configurations.database import engine
from app.models import User, ValidToken
from app.packages.Auth import (
    verify_password,
    create_token,
    decode_token,
    decode_header_token,
    is_token_valid,
)

router = APIRouter(prefix="/v1")


# UserLogin é um JSON com email e senha;
class UserLogin(BaseModel):
    email: str
    password: str


@router.post("/login")
async def authenticate_user(request: UserLogin = Body(...)) -> JSONResponse:
    with Session(engine) as session:
        user_exists = session.query(User).filter(
            User.email == request.email).first()

        if user_exists is not None:
            valid_password = verify_password(
                request.password, user_exists.password)

        if user_exists is None or not valid_password:
            raise HTTPException(
                detail={
                    "error": {
                        "message": "Password or email entered is not valid. Try again.",
                        "type": "UserError",
                        "code": 401
                    }
                },
                status_code=status.HTTP_401_UNAUTHORIZED,
                headers={"WWW-Authenticate": "Bearer"}
            )

        access_token = create_token(user_exists, "access")
        refresh_token = create_token(user_exists, "refresh")
        user = decode_token(access_token)
        del user["exp"]

        valid_token = session.query(ValidToken).filter(
            ValidToken.user_id == user_exists.id).first()

        if valid_token:
            access_token_valid = is_token_valid(
                valid_token.access_expiration_date)
            refresh_token_valid = is_token_valid(
                valid_token.refresh_expiration_date)

            if access_token_valid and refresh_token_valid:
                return JSONResponse({
                    "user": user,
                    "access_token": valid_token.access_token_id,
                    "refresh_token": valid_token.refresh_token_id,
                    "token_type": "bearer"
                })

            if not access_token_valid and not refresh_token_valid:
                valid_token = ValidToken(
                    user_id=user_exists.id,
                    access_token_id=access_token,
                    refresh_token_id=refresh_token,
                    access_expiration_date=datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRES),
                    refresh_expiration_date=datetime.utcnow() + timedelta(hours=REFRESH_TOKEN_EXPIRES),
                )
            elif not access_token_valid and refresh_token_valid:
                valid_token.access_token_id = access_token
                valid_token.access_expiration_date = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRES)
                valid_token.updated_at = datetime.utcnow()
        else:
            valid_token = ValidToken(
                user_id=user_exists.id,
                access_token_id=access_token,
                refresh_token_id=refresh_token,
                access_expiration_date=datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRES),
                refresh_expiration_date=datetime.utcnow() + timedelta(hours=REFRESH_TOKEN_EXPIRES),
            )

        session.add(valid_token)
        session.commit()

        return JSONResponse({
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        })


@router.post('/logout')
async def logout(request: dict = Depends(decode_header_token)) -> JSONResponse:
    with Session(engine) as session:
        valid_token = session.query(ValidToken).filter(
            ValidToken.user_id == request["id"]).first()

        if not valid_token:
            raise HTTPException(
                detail={
                    "error": {
                        "message": "You must be authenticated to make a request for a logout route. User not identified or with invalid token.",
                        "type": "UserError",
                        "code": 401
                    }
                },
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        session.query(ValidToken).filter(
            ValidToken.user_id == request["id"]).delete()
        session.commit()

        return JSONResponse({
            "success": {
                "message": "You have successfully logged in. See you soon.",
                "type": "UserInfo",
                "code": 200
            }
        })


@router.post('/refresh')
async def refresh_token(request: dict = Depends(decode_header_token)) -> JSONResponse:
    with Session(engine) as session:
        user = session.query(User).filter(User.id == request["id"]).first()
        refresh_token = session.query(ValidToken).filter(
            ValidToken.user_id == user.id,
            ValidToken.refresh_expiration_date >= datetime.utcnow()
        ).first()

        if refresh_token:
            refresh_token_payload = decode_token(
                refresh_token.refresh_token_id)
            if refresh_token_payload.get("id") != user.id:
                raise HTTPException(
                    detail={
                        "error": {
                            "message": "The informed token does not belong to the user in question.",
                            "type": "UserError",
                            "type": 401
                        }
                    },
                    status_code=status.HTTP_401_UNAUTHORIZED
                )

            new_access_token = create_token(user, "access")
            access_token_payload = decode_token(new_access_token)
            access_expiration_date = datetime.fromtimestamp(
                access_token_payload.get("exp"))

            refresh_token.access_token_id = new_access_token
            refresh_token.access_expiration_date = access_expiration_date
            session.commit()

            user = decode_token(new_access_token)

            return JSONResponse({
                "user": user,
                "access_token": new_access_token,
                "token_type": "bearer"
            })

        else:
            raise HTTPException(
                detail={
                    "error": {
                        "message": "No valid refresh token was found.",
                        "type": "UserError",
                        "code": 404
                    }
                },
                status_code=status.HTTP_404_NOT_FOUND
            )
