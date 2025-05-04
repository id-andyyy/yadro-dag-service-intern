import pytest
from fastapi.testclient import TestClient


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
        ([{"name": "a"}, {"name": "b"}], [{"source": "a", "target": "b"}]),
        ([{"name": "a"}, {"name": "b"}, {"name": "c"}], []),
        ([{"name": "a"}], []),
    ], ids=[
        "simple-graph",
        "no-edges",
        "one-node",
    ]
)
def test_create_and_read_graph(client: TestClient,
                               nodes: list[dict[str, str]],
                               edges: list[dict[str, str]]):
    response = client.post("/api/graph", json={"nodes": nodes, "edges": edges})
    assert response.status_code == 201
    graph_id = response.json()["id"]

    response = client.get(f"/api/graph/{graph_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["nodes"] == nodes
    assert data["edges"] == edges


@pytest.mark.parametrize(
    "nodes, edges, expected_status",
    [
        ([{"name": "a"}, {"name": "b"}], [{"source": "c", "target": "d"}], 400),
        ([{"name": "a"}, {"name": "b"}], [{"source": "a", "target": "c"}], 400),
        ([], [], 400),
        ([], [{"source": "a", "target": "b"}], 400),
        ([{"name": "a1"}, {"name": "b1"}], [{"source": "a1", "target": "b1"}], 400),
        ([{"name": "a_a"}, {"name": "b_b"}], [{"source": "a_a", "target": "b_b"}], 400),
        ([{"name": "a"}, {"name": "a"}, {"name": "b"}], [{"source": "a", "target": "b"}], 400),
        ([{"name": "a"}, {"name": "b"}], [{"source": "a", "target": "b"}, {"source": "a", "target": "b"}], 400),
        ([{"name": ""}, {"name": "b"}], [{"source": "", "target": "b"}], 400),
        ([{"name": "a" * 256}, {"name": "b"}], [{"source": "a" * 256, "target": "b"}], 400),
        ([{"name": "a"}, {"name": "b"}, {"name": "c"}],
         [{"source": "a", "target": "b"}, {"source": "b", "target": "c"}, {"source": "c", "target": "a"}], 400),

        ([{"name": 1}, {"name": "b"}], [{"source": 1, "target": "b"}], 422),
        ([{"title": 1}, {"title": "b"}], [{"source": 1, "target": "b"}], 422),
        ([{"name": 1}, {"name": "b"}], [{"from": 1, "to": "b"}], 422),
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
                              nodes: list[dict[str, str]],
                              edges: list[dict[str, str]],
                              expected_status):
    response = client.post("/api/graph", json={"nodes": nodes, "edges": edges})
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "path, expected_status",
    [
        ("/api/graph/100", 404),
        ("/api/graph/0", 404),
        ("/api/graph/invalid", 422),
    ], ids=[
        "not-found-id",
        "zero-id",
        "invalid-id-format",
    ]
)
def test_read_graph_invalid(client: TestClient, path: str, expected_status: int):
    response = client.get(path)
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
                            nodes: list[dict[str, str]],
                            edges: list[dict[str, str]],
                            expected_adj: dict[str, list[str]]):
    payload = {"nodes": [{"name": node} for node in nodes],
               "edges": [{"source": source, "target": target} for (source, target) in edges]}
    response = client.post("/api/graph", json=payload)
    assert response.status_code == 201
    graph_id: int = response.json()["id"]

    response = client.get(f"/api/graph/{graph_id}/adjacency_list")
    assert response.status_code == 200

    data = response.json()
    assert "adjacency_list" in data
    assert data["adjacency_list"] == expected_adj


@pytest.mark.parametrize(
    "path, expected_status",
    [
        ("/api/graph/100/adjacency_list", 404),
        ("/api/graph/0/adjacency_list", 404),
        ("/api/graph/invalid/adjacency_list", 422),
    ], ids=[
        "not-found-id",
        "zero-id",
        "invalid-id-format",
    ]
)
def test_get_adjacency_list_invalid(client: TestClient, path: str, expected_status: int):
    response = client.get(path)
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
                                    nodes: list[dict[str, str]],
                                    edges: list[dict[str, str]],
                                    expected_adj: dict[str, list[str]]):
    payload = {"nodes": [{"name": node} for node in nodes],
               "edges": [{"source": source, "target": target} for (source, target) in edges]}
    response = client.post("/api/graph", json=payload)
    assert response.status_code == 201
    graph_id = response.json()["id"]

    response = client.get(f"/api/graph/{graph_id}/reverse_adjacency_list")
    assert response.status_code == 200

    data = response.json()
    assert "adjacency_list" in data
    assert data["adjacency_list"] == expected_adj


@pytest.mark.parametrize(
    "path, expected_status",
    [
        ("/api/graph/100/reverse_adjacency_list", 404),
        ("/api/graph/0/reverse_adjacency_list", 404),
        ("/api/graph/invalid/reverse_adjacency_list", 422),
    ], ids=[
        "not-found-id",
        "zero-id",
        "invalid-id-format",
    ]
)
def test_get_reverse_adjacency_list_invalid(client: TestClient, path: str, expected_status: int):
    response = client.get(path)
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
    payload = {"nodes": [{"name": node} for node in nodes],
               "edges": [{"source": source, "target": target} for (source, target) in edges]}
    response = client.post("/api/graph", json=payload)
    assert response.status_code == 201
    graph_id = response.json()["id"]

    response = client.delete(f"/api/graph/{graph_id}/node/{node_name}")
    assert response.status_code == 204

    response = client.get(f"/api/graph/{graph_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["nodes"] == [{"name": node} for node in result_nodes]
    assert data["edges"] == [{"source": source, "target": target} for (source, target) in result_edges]
