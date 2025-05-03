import pytest
from sqlalchemy.orm import Session

from app.models.graph import Graph
from app.crud.graph import db_create_graph, db_get_graph_by_id
from string import ascii_lowercase
from itertools import product


def test_crud_create_and_get_graph(db_session: Session):
    names = ["a", "b", "c"]
    edges = [("a", "b"), ("b", "c")]

    graph: Graph = db_create_graph(db_session, names, edges)
    assert isinstance(graph.id, int)

    fetched = db_get_graph_by_id(db_session, graph.id)
    assert fetched is not None
    assert fetched.id == graph.id

    fetched_nodes = {node.name for node in fetched.nodes}
    assert fetched_nodes == set(names)

    fetched_edges = {(edge.source, edge.target) for edge in fetched.edges}
    assert fetched_edges == set(edges)


@pytest.mark.load
def test_bulk_create_graph(db_session: Session):
    for _ in range(1000):
        names = ["".join(letters) for letters in product(ascii_lowercase[:10], repeat=2)]
        edges = []
        for i in range(len(names)):
            for j in range(i + 1, min(len(names), i + 12)):
                edges.append((names[i], names[j]))

        graph: Graph = db_create_graph(db_session, names, edges)
        assert isinstance(graph.id, int)
