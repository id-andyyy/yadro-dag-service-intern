import uvicorn
from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine
from app.models.graph import Graph, Node, Edge
from app.routers import router as graph_router

app = FastAPI()

app.include_router(graph_router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/healthz")
def health_check():
    return {"status": "ok"}
