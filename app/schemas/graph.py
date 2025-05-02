from pydantic import BaseModel


class Node(BaseModel):
    name: str


class Edge(BaseModel):
    source: str
    target: str


class GraphCreate(BaseModel):
    nodes: list[Node]
    edges: list[Edge]


class GraphCreateResponse(BaseModel):
    id: int


class GraphReadResponse(BaseModel):
    id: int
    nodes: list[Node]
    edges: list[Edge]
