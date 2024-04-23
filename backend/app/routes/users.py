from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.param_functions import Body
from fastapi.responses import JSONResponse

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlmodel import select
from typing import List
from pydantic import BaseModel

from app.configurations.database import engine
from app.models import User
from app.packages.Auth import get_current_user, is_user_administrator

router = APIRouter(prefix="/v1")


class UserCreate(BaseModel):
    name: str
    username: str
    email: str
    password: str


@router.get('/users/me')
async def get_me(user: User = Depends(get_current_user)) -> JSONResponse:
    user_data = {
        "id": user.id,
        "name": user.name,
        "username": user.username,
        "email": user.email,
        "type": user.type
    }

    return JSONResponse({"user": user_data}, status.HTTP_200_OK)


@router.get('/users/{id}')
async def get_user_by_id(id: int, user: User = Depends(is_user_administrator)) -> JSONResponse:
    with Session(engine) as session:
        user_data = session.get(User, id)
        if not user_data:
            raise HTTPException(
                detail={"error": {"message": "User not found.",
                                  "type": "UserError", "code": 404}},
                status_code=status.HTTP_404_NOT_FOUND
            )
        return JSONResponse({"user": user_data}, status.HTTP_200_OK)


@router.get('/users', response_model=List[User])
async def get_users(user: User = Depends(is_user_administrator)) -> JSONResponse:
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        users_count = len(users)
        return JSONResponse({"users": users, "users_count": users_count}, status.HTTP_200_OK)


@router.post('/users', response_model=dict)
async def create_user(user: UserCreate = Body(...)) -> JSONResponse:
    with Session(engine) as session:
        try:
            new_user = User(**user.dict())
            new_user.set_password(user.password)

            session.add(new_user)
            session.commit()

            return JSONResponse({
                "success": {"message": "User created successfully.", "type": "UserInfo", "code": 201}
            }, status.HTTP_201_CREATED)
        except IntegrityError:
            session.rollback()
            raise HTTPException(
                detail={"error": {"message": "User already exists.",
                                  "type": "UserError", "code": 409}},
                status_code=status.HTTP_409_CONFLICT
            )


@router.patch('/users', response_model=dict)
async def update_user(updated_user: UserCreate, current_user: User = Depends(get_current_user)) -> JSONResponse:
    with Session(engine) as session:
        existing_user = session.get(User, updated_user.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                detail={"error": {
                    "message": "User with this email already exists.", "type": "UserError", "code": 409}},
                status_code=status.HTTP_409_CONFLICT
            )
        current_user.name = updated_user.name
        current_user.username = updated_user.username
        current_user.email = updated_user.email
        current_user.set_password(updated_user.password)
        session.add(current_user)
        session.commit()
        return JSONResponse({
            "success": {"message": "User information updated successfully.", "type": "UserInfo", "code": 200}
        }, status.HTTP_200_OK)


@router.delete('/users/{id}')
async def delete_user(id: int, user: User = Depends(is_user_administrator)) -> JSONResponse:
    with Session(engine) as session:
        user_to_delete = session.get(User, id)
        if not user_to_delete:
            raise HTTPException(
                detail={"error": {"message": f"No user found with ID {
                    id}.", "type": "UserError", "code": 404}},
                status_code=status.HTTP_404_NOT_FOUND
            )
        session.delete(user_to_delete)
        session.commit()
        return JSONResponse({
            "success": {"message": f"User with ID {id} successfully deleted.", "type": "UserInfo", "code": 200}
        }, status.HTTP_200_OK)
