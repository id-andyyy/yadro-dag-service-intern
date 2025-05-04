import pytest
from sqlalchemy.orm import Session

from app.models.graph import Graph
from app.crud.graph import db_create_graph, db_get_graph_by_id, db_delete_node, NotFoundError
from string import ascii_lowercase
from itertools import product


@pytest.mark.parametrize(
    "names, edges",
    [
        (["a", "b", "c"], [("a", "b"), ("b", "c")]),
        (["a", "b", "c"], [("a", "b"), ("a", "c")]),
        (["a"], []),
    ], ids=[
        "simple-graph",
        "star",
        "no-edges",
    ]
)
def test_crud_create_and_get_graph(db_session: Session, names: list[str], edges: list[tuple[str, str]]):
    graph: Graph = db_create_graph(db_session, names, edges)
    assert isinstance(graph.id, int)

    fetched = db_get_graph_by_id(db_session, graph.id)
    assert fetched is not None
    assert fetched.id == graph.id

    fetched_nodes = {node.name for node in fetched.nodes}
    assert fetched_nodes == set(names)

    fetched_edges = {(edge.source, edge.target) for edge in fetched.edges}
    assert fetched_edges == set(edges)


@pytest.mark.parametrize(
    "graph_id, error, error_message",
    [
        (100, NotFoundError, "Graph not found"),
        (0, NotFoundError, "Graph not found"),
    ], ids=[
        "graph-not-found",
        "zero-id",
    ]
)
def test_crud_get_invalid_graph(db_session: Session, graph_id: int, error: Exception, error_message: str):
    with pytest.raises(NotFoundError) as exc_info:
        db_get_graph_by_id(db_session, graph_id=graph_id)

    assert exc_info.type is error
    assert str(exc_info.value) == error_message


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


# @pytest.mark.parametrize(
#     "names, edges, graph_id, node_id",
#     [
#         (["a", "b"])
#     ]
# )
# def test_crud_delete_node(db_session: Session):
