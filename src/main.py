from src.utils.db.base import Base
from fastapi import FastAPI
from src.utils.db.session import Engine
from src.models.models import *
from src.User.router import router as UserRouter

app = FastAPI()

# Bind Base & Engine
Base.metadata.create_all(Engine)



@app.get("/")
def read_root():
    return {"Hello": "World"}


app.include_router(UserRouter)