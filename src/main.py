from src.utils.db.base import Base
from fastapi import FastAPI
from src.utils.db.session import Engine
from src.models.models import *

app = FastAPI()

# Bind Base & Engine
Base.metadata.create_all(Engine)



@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}