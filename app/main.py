from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine
from app.models.graph import Graph, Node, Edge
from app.routers import router as graph_router
from contextlib import asynccontextmanager

app: FastAPI = FastAPI()
app.include_router(graph_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
