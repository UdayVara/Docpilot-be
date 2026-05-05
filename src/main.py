from src.utils.db.base import Base
from fastapi import FastAPI
from src.utils.db.session import Engine
from src.models.models import *
from src.User.router import router as UserRouter
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Bind Base & Engine
Base.metadata.create_all(Engine)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


app.include_router(UserRouter)