from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.param_functions import Body
from sqlmodel import select

from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.models import User, UserTweet, Tweet
from app.packages.Auth import get_current_user, is_user_administrator
from app.configurations.database import engine


class TweetCreate(BaseModel):
    text: str


router = APIRouter(prefix="/v1")


@router.get('/tweets')
async def get_all_tweets(user: User = Depends(get_current_user)) -> JSONResponse:
    with Session(engine) as session:
        tweets = session.query(Tweet).all()
        serialized_tweets = jsonable_encoder(tweets)

        return JSONResponse(content={"tweets": serialized_tweets}, status_code=status.HTTP_200_OK)


@router.get('/tweets/me')
async def get_user_tweets(user: User = Depends(get_current_user)) -> JSONResponse:
    with Session(engine) as session:
        tweets = session.query(Tweet).filter(Tweet.user_id == user.id).all()

        tweet_list = [jsonable_encoder(t) for t in tweets]

        return JSONResponse({"user_id": user.id, "tweets": tweet_list}, status_code=status.HTTP_200_OK)


@router.get('/tweets/{id}')
async def get_tweet(id: int, user: User = Depends(get_current_user)) -> JSONResponse:
    with Session(engine) as session:
        tweet = session.query(Tweet).filter(Tweet.id == id).first()

        if not tweet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"message": f"No tweet with identifier {
                    id} was found.", "type": "TweetError"}}
            )
        return JSONResponse(content={"tweet": tweet})


@router.post('/tweets')
async def create_tweet(
        tweet: TweetCreate = Body(...),
        user: User = Depends(get_current_user)) -> JSONResponse:
    with Session(engine) as session:
        new_tweet = Tweet(**tweet.dict())
        new_tweet.user_id = user.id
        session.add(new_tweet)
        session.commit()
        return JSONResponse(
            content={"success": {
                "message": "Tweet created successfully", "type": "TweetInfo"}},
            status_code=status.HTTP_201_CREATED
        )


@router.patch('/tweets/{id}')
async def update_tweet(
        id: int, tweet: TweetCreate,
        user: User = Depends(is_user_administrator)) -> JSONResponse:
    with Session(engine) as session:
        existing_tweet = session.query(Tweet).filter(Tweet.id == id).first()
        if not existing_tweet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"message": f"No tweet with identifier {
                    id} was found.", "type": "TweetError"}}
            )
        for field, value in tweet.dict(exclude_unset=True).items():
            setattr(existing_tweet, field, value)
        session.commit()
        return JSONResponse(
            content={"success": {
                "message": "Tweet updated successfully", "type": "TweetInfo"}},
            status_code=status.HTTP_200_OK
        )


@router.delete('/tweets/{id}')
async def delete_tweet(
        id: int,
        user: User = Depends(is_user_administrator)) -> JSONResponse:
    with Session(engine) as session:
        existing_tweet = session.query(Tweet).filter(Tweet.id == id).first()
        if not existing_tweet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tweet not found"
            )
        session.delete(existing_tweet)
        session.commit()
        return JSONResponse(
            content={"success": {
                "message": "Tweet deleted successfully", "type": "TweetInfo"}},
            status_code=status.HTTP_200_OK
        )

# TODO: Rotas para o usuário deletar ou alterar o seu próprio tweet.
