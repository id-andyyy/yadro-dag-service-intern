from fastapi import APIRouter

from app.routers.graph import router as graph_router

main_router = APIRouter()
main_router.include_router(graph_router)
