from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine
from app.models.graph import Graph

app = FastAPI()


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/healthz")
async def health_check():
    return {"status": "ok"}
