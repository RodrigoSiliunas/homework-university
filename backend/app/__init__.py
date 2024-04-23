from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlmodel import SQLModel
from app.models import (
    User,
    Tweet,
    UserTweet,
    ValidToken
)

from app.configurations.database import engine

# Área de importação de rotas:
from app.routes import (
    users,
    accounts,
    tweets
)

"""
==========================================================================
 ➠ Backend of Twitter
 ➠ Section By: Fabricio Abreu
 ➠ Related system: Core da aplicação do Twitter
==========================================================================
"""

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# Lógica para inicialização do nosso banco de dados;
# TODO: Fazer a verificação, caso as tabelas já estejam criadas não tentar criar novamente.
SQLModel.metadata.create_all(engine)

# Registro das minhas rotas:
app.include_router(users)
app.include_router(tweets)
app.include_router(accounts)