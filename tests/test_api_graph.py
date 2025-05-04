import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError


def get_dict_data(nodes: list[str], edges: list[tuple[str, str]]) -> dict[str, list[dict[str, str]]]:
    return {"nodes": [{"name": node} for node in nodes],
            "edges": [{"source": source, "target": target} for (source, target) in edges]}


@pytest.mark.parametrize(
    "path, body",
    [
        ("/health", {"status": "ok"}),
    ], ids=[
        "health-root"
    ]
)
def test_health_check(client: TestClient, path: str, body: dict[str, dict[str, str]]):
    response = client.get(path)
    assert response.status_code == 200
    assert response.json() == body


@pytest.mark.parametrize(
    "nodes, edges",
    [
        (["a", "b"], [("a", "b")]),
        (["a", "b", "c"], []),
        (["a"], []),
    ], ids=[
        "simple-graph",
        "no-edges",
        "one-node",
    ]
)
def test_create_and_read_graph(client: TestClient,
                               nodes: list[str],
                               edges: list[tuple[str, str]]):
    payload = get_dict_data(nodes, edges)
    response = client.post("/api/graph", json=payload)
    assert response.status_code == 201
    graph_id = response.json()["id"]

    response = client.get(f"/api/graph/{graph_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["nodes"] == payload["nodes"]
    assert data["edges"] == payload["edges"]


@pytest.mark.parametrize(
    "nodes, edges",
    [
        (["a", "b"], [("a", "b")]),
    ], ids=[
        "simple-graph",
    ]
)
def test_db_integrity_error_returns_400(client: TestClient,
                                        monkeypatch: pytest.MonkeyPatch,
                                        nodes: list[str],
                                        edges: list[tuple[str, str]]):
    payload = get_dict_data(nodes, edges)

    def fake_db_create_graph(db, names, edges):
        raise IntegrityError("orig statement", params=None, orig=None)

    monkeypatch.setattr("app.routers.graph.db_create_graph", fake_db_create_graph)

    response = client.post("/api/graph/", json=payload)

    assert response.status_code == 400
    body = response.json()
    assert "message" in body
    assert "Database integrity error" in body["message"]


@pytest.mark.parametrize(
    "nodes, edges, expected_status",
    [
        (["a", "b"], [("c", "d")], 400),
        (["a", "b"], [("a", "c")], 400),
        ([], [], 400),
        ([], [("a", "b")], 400),
        (["a1", "b1"], [("a1", "b1")], 400),
        (["a_a", "b_b"], [("a_a", "b_b")], 400),
        (["a", "a", "b"], [("a", "b")], 400),
        (["a", "b"], [("a", "b"), ("a", "b")], 400),
        (["", "b"], [("", "b")], 400),
        (["a" * 256, "b"], [("a" * 256, "b")], 400),
        (["a", "b", "c"], [("a", "b"), ("b", "c"), ("c", "a")], 400),

        ([1, "b"], [(1, "b")], 422),
        ([1, "b"], [(1, "b")], 422),
        ([1, "b"], [(1, "b")], 422),
    ], ids=[
        "edge-nodes-not-existent",
        "edge-target-missing-node",
        "no-nodes",
        "no-nodes-with-edges",
        "invalid-char-in-name-digit",
        "invalid-char-in-name-underscore",
        "duplicate-node-names",
        "duplicate-edges",
        "empty-name",
        "name-too-long",
        "three-node-cycle",

        "wrong-type-in-node-and-edges",
        "wrong-node-title",
        "wrong-edge-title",
    ]
)
def test_create_graph_invalid(client: TestClient,
                              nodes: list[str],
                              edges: list[tuple[str, str]],
                              expected_status):
    response = client.post("/api/graph", json=get_dict_data(nodes, edges))
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "graph_id, expected_status",
    [
        (100, 404),
        (0, 404),
        ("invalid", 422),
    ], ids=[
        "not-found-id",
        "zero-id",
        "invalid-id-format",
    ]
)
def test_read_graph_invalid(client: TestClient, graph_id: int | str, expected_status: int):
    response = client.get(f"/api/graph/{graph_id}")
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "nodes, edges, expected_adj",
    [
        (
                ["a", "b", "c"],
                [("a", "b"), ("b", "c")],
                {"a": ["b"], "b": ["c"], "c": []}
        ),
        (
                ["a", "b", "c", "d"],
                [("a", "b"), ("a", "c"), ("a", "d")],
                {"a": ["b", "c", "d"], "b": [], "c": [], "d": []}
        ),
        (
                ["a", "b"],
                [],
                {"a": [], "b": []}
        ),
    ], ids=[
        "chain",
        "star",
        "no-edges"
    ]
)
def test_get_adjacency_list(client: TestClient,
                            nodes: list[str],
                            edges: list[tuple[str, str]],
                            expected_adj: dict[str, list[str]]):
    response = client.post("/api/graph", json=get_dict_data(nodes, edges))
    assert response.status_code == 201
    graph_id: int = response.json()["id"]

    response = client.get(f"/api/graph/{graph_id}/adjacency_list")
    assert response.status_code == 200

    data = response.json()
    assert "adjacency_list" in data
    assert data["adjacency_list"] == expected_adj


@pytest.mark.parametrize(
    "graph_id, expected_status",
    [
        (100, 404),
        (0, 404),
        ("invalid", 422),
    ], ids=[
        "not-found-id",
        "zero-id",
        "invalid-id-format",
    ]
)
def test_get_adjacency_list_invalid(client: TestClient, graph_id: int | str, expected_status: int):
    response = client.get(f"/api/graph/{graph_id}/adjacency_list")
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "nodes, edges, expected_adj",
    [
        (
                ["a", "b", "c"],
                [("a", "b"), ("b", "c")],
                {"a": [], "b": ["a"], "c": ["b"]}
        ),
        (
                ["a", "b", "c", "d"],
                [("a", "b"), ("a", "c"), ("a", "d")],
                {"a": [], "b": ["a"], "c": ["a"], "d": ["a"]}
        ),
        (
                ["a", "b"],
                [],
                {"a": [], "b": []}
        ),
    ], ids=[
        "chain",
        "star",
        "no-edges"
    ]
)
def test_get_reverse_adjacency_list(client: TestClient,
                                    nodes: list[str],
                                    edges: list[tuple[str, str]],
                                    expected_adj: dict[str, list[str]]):
    response = client.post("/api/graph", json=get_dict_data(nodes, edges))
    assert response.status_code == 201
    graph_id = response.json()["id"]

    response = client.get(f"/api/graph/{graph_id}/reverse_adjacency_list")
    assert response.status_code == 200

    data = response.json()
    assert "adjacency_list" in data
    assert data["adjacency_list"] == expected_adj


@pytest.mark.parametrize(
    "graph_id, expected_status",
    [
        (100, 404),
        (0, 404),
        ("invalid", 422),
    ], ids=[
        "not-found-id",
        "zero-id",
        "invalid-id-format",
    ]
)
def test_get_reverse_adjacency_list_invalid(client: TestClient, graph_id: int | str, expected_status: int):
    response = client.get(f"/api/graph/{graph_id}/reverse_adjacency_list")
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "nodes, edges, node_name, result_nodes, result_edges",
    [
        (
                ["a", "b", "c"],
                [("a", "b"), ("b", "c")],
                "a",
                ["b", "c"], [("b", "c")]
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
def test_delete_node(client: TestClient,
                     nodes: list[str],
                     edges: list[tuple[str, str]],
                     node_name: str,
                     result_nodes: list[str],
                     result_edges: list[tuple[str, str]]):
    payload = get_dict_data(nodes, edges)
    response = client.post("/api/graph", json=payload)
    assert response.status_code == 201
    graph_id = response.json()["id"]

    response = client.delete(f"/api/graph/{graph_id}/node/{node_name}")
    assert response.status_code == 204

    response = client.get(f"/api/graph/{graph_id}")
    assert response.status_code == 200
    data = response.json()

    result = get_dict_data(result_nodes, result_edges)
    assert data["nodes"] == result["nodes"]
    assert data["edges"] == result["edges"]


@pytest.mark.parametrize(
    "nodes, edges, graph_id, node_name, expected_status",
    [
        (["a", "b"], [("a", "b")], 100, "a", 404),
        (["a", "b"], [("a", "b")], 0, "a", 404),
        (["a", "b"], [("a", "b")], 1, "x", 404),
        (["a"], [], 1, "a", 422),
        (["a", "b"], [("a", "b")], "invalid", "invalid", 422),
    ], ids=[
        "non-existent-graph-id",
        "zero-graph-id",
        "non-existent-node",
        "graph-with-single-node",
        "invalid-graph-id",
    ]
)
def test_delete_node_invalid(client: TestClient,
                             nodes: list[str],
                             edges: list[tuple[str, str]],
                             graph_id: int | str,
                             node_name: str,
                             expected_status: int):
    payload = {"nodes": [{"name": node} for node in nodes],
               "edges": [{"source": source[0], "target": target} for (source, target) in edges]}
    response = client.post(f"/api/graph", json=payload)
    assert response.status_code == 201

    response = client.delete(f"/api/graph/{graph_id}/node/{node_name}")
    assert response.status_code == expected_status
