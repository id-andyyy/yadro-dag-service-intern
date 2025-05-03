from fastapi import APIRouter, Depends, status

from app.schemas.graph import GraphCreate, GraphCreateResponse, GraphReadResponse
from app.schemas.common import ErrorResponse
from app.db.deps import get_db
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from app.utils.graph import detect_cycles
from app.crud.graph import db_create_graph, db_get_graph_by_id, NotFoundError
import re

router = APIRouter()


@router.post(
    "/api/graph/",
    response_model=GraphCreateResponse,
    status_code=status.HTTP_201_CREATED,
    description="Ручка для создания графа, принимает граф в виде списка вершин и списка ребер",
    responses={
        400: {"model": ErrorResponse, "description": "Failed to add graph"},
    }, )
def create_graph(graph_in: GraphCreate, db: Session = Depends(get_db)):
    node_names = [node.name for node in graph_in.nodes]
    edges = [(edge.source, edge.target) for edge in graph_in.edges]

    if not node_names:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "There must be at least one node"},
        )

    for name in node_names:
        if not (1 <= len(name)):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": f"Node name '{name}' must be at least 1 character long"},
            )
        if not (len(name) <= 255):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": f"Node name '{name}' must be at most 255 characters long"},
            )
        if not re.match(r'^[a-zA-Z]+$', name):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": f"Node name '{name}' must consist only of Latin letters"},
            )
    if len(node_names) != len(set(node_names)):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Node names must be unique"},
        )

    for source, target in edges:
        if source not in node_names or target not in node_names:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": f"Edge ({source}->{target}) with a non-existent vertex"},
            )

    seen = set()
    for source, target in edges:
        if (source, target) in seen:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": f"Duplicate edge ({source}->{target})"},
            )
        seen.add((source, target))

    if detect_cycles(node_names, edges):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Graph must not contain cycles"},
        )

    new_graph = db_create_graph(db, node_names, edges)
    return GraphCreateResponse(id=new_graph.id)


@router.get(
    "/api/graph/{graph_id}/",
    response_model=GraphReadResponse,
    status_code=status.HTTP_200_OK,
    description="Ручка для чтения графа в виде списка вершин и списка ребер",
    responses={
        400: {"model": ErrorResponse, "description": "Graph entity not found"},
    }
)
def read_graph(graph_id: int, db: Session = Depends(get_db)):
    try:
        graph = db_get_graph_by_id(db, graph_id)
    except NotFoundError as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": str(e)},
        )
    return GraphReadResponse.model_validate(graph, from_attributes=True)
