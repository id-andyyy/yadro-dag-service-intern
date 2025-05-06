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


@pytest.mark.parametrize(
    "nodes, edges, node_name, result_nodes, result_edges",
    [
        (
                ["a", "b", "c"],
                [("a", "b"), ("b", "c")],
                "a",
                ["b", "c"],
                [("b", "c")]
        ),
        (
                ["a", "b", "c", "d"],
                [("a", "b"), ("a", "c"), ["a", "d"]],
                "a",
                ["b", "c", "d"],
                []
        ),
        (
                ["a", "b"],
                [],
                "a",
                ["b"],
                []
        ),
        (
                ["a", "b", "c", "d", "e"],
                [("a", "b"), ("b", "c"), ("c", "d"), ("d", "e")],
                "c",
                ["a", "b", "d", "e"],
                [("a", "b"), ("d", "e")]
        ),
        (
                ["a", "b", "c", "d", "e"],
                [("d", "c"), ("d", "a"), ("b", "e")],
                "d",
                ["a", "b", "c", "e"],
                [("b", "e")]
        ),
        (
                ["a", "b", "c"],
                [("a", "b")],
                "c",
                ["a", "b"],
                [("a", "b")]
        ),
    ], ids=[
        "simple-graph",
        "star",
        "no-edges",
        "chain",
        "last-node",
        "node-without-edges",
    ]
)
def test_crud_delete_node(db_session: Session,
                          nodes: list[str],
                          edges: list[tuple[str, str]],
                          node_name: str,
                          result_nodes: list[str],
                          result_edges: list[tuple[str, str]]):
    graph: Graph = db_create_graph(db_session, nodes, edges)

    db_delete_node(db_session, graph.id, node_name)

    result_graph = db_get_graph_by_id(db_session, graph.id)
    assert result_graph is not None
    assert {node.name for node in result_graph.nodes} == set(result_nodes)
    assert {(edge.source, edge.target) for edge in result_graph.edges} == set(result_edges)


@pytest.mark.parametrize(
    "nodes, edges, graph_id, node_name, error, error_message",
    [
        (["a", "b", "c"], [("a", "b"), ("b", "c")], 1, "d", NotFoundError, "Node not found"),
        (["a", "b"], [("a", "b")], 100, "a", NotFoundError, "Graph not found"),
    ], ids=[
        "invalid-node-name",
        "invalid-graph-id",
    ]
)
def test_crud_delete_invalid_node(db_session: Session,
                                  nodes: list[str],
                                  edges: list[tuple[str, str]],
                                  graph_id: int,
                                  node_name: str,
                                  error: Exception,
                                  error_message: str):
    graph: Graph = db_create_graph(db_session, nodes, edges)

    with pytest.raises(NotFoundError) as exc_info:
        db_delete_node(db_session, graph_id=graph_id, node_name=node_name)

    assert exc_info.type is error
    assert str(exc_info.value) == error_message
