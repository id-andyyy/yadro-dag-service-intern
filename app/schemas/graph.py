from pydantic import BaseModel
from typing import List


class NodeCreate(BaseModel):
    name: str


class EdgeCreate(BaseModel):
    source: str
    target: str


class GraphCreate(BaseModel):
    nodes: List[NodeCreate]
    edges: List[EdgeCreate]
