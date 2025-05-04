import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    "path, status, body",
    [
        ("/health", 200, {"status": "ok"}),
    ], ids=[
        "health-root"
    ]
)
def test_health_check(client: TestClient, path, status, body):
    response = client.get(path)
    assert response.status_code == status
    assert response.json() == body


@pytest.mark.parametrize(
    "nodes, edges, create_status, read_status",
    [
        ([{"name": "a"}, {"name": "b"}], [{"source": "a", "target": "b"}], 201, 200),
        ([{"name": "a"}, {"name": "b"}, {"name": "c"}], [], 201, 200),
        ([{"name": "a"}], [], 201, 200),
    ], ids=[
        "simple-graph",
        "no-edges",
        "one-node",
    ]
)
def test_create_and_read_graph(client: TestClient,
                               nodes: list[dict[str, str]],
                               edges: list[dict[str, str]],
                               create_status: int,
                               read_status: int):
    post = client.post("/api/graph/", json={"nodes": nodes, "edges": edges})
    assert post.status_code == create_status
    graph_id = post.json()["id"]

    get = client.get(f"/api/graph/{graph_id}/")
    assert get.status_code == read_status
    data = get.json()
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

        "wrong-type-in-node-and-edges",
        "wrong-node-title",
        "wrong-edge-title",
    ]
)
def test_create_invalid_graph(client: TestClient,
                              nodes: list[dict[str, str]],
                              edges: list[dict[str, str]],
                              expected_status):
    response = client.post("/api/graph/", json={"nodes": nodes, "edges": edges})
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "path, expected_status",
    [
        ("/api/graph/100/", 404),
        ("/api/graph/0/", 404),
        ("/api/graph/invalid/", 422),
    ], ids=[
        "not-found-id",
        "zero-id",
        "invalid-id-format",
    ]
)
def test_read_invalid_graph(client: TestClient, path: str, expected_status: int):
    response = client.get(path)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "nodes, edges, status, expected_adj",
    [
        (
                [{"name": "a"}, {"name": "b"}, {"name": "c"}],
                [{"source": "a", "target": "b"}, {"source": "b", "target": "c"}],
                200,
                {"a": ["b"], "b": ["c"], "c": []}
        ),
        (
                [{"name": "a"}, {"name": "b"}, {"name": "c"}, {"name": "d"}],
                [{"source": "a", "target": "b"}, {"source": "a", "target": "c"}, {"source": "a", "target": "d"}],
                200,
                {"a": ["b", "c", "d"], "b": [], "c": [], "d": []}
        ),
        (
                [{"name": "a"}, {"name": "b"}],
                [],
                200,
                {"a": [], "b": []}
        ),
    ], ids=[
        "chain",
        "star",
        "no-edges"
    ]
)
def test_read_graph_adjacency_list(client: TestClient,
                                   nodes: list[dict[str, str]],
                                   edges: list[dict[str, str]],
                                   status: int,
                                   expected_adj: dict[str, list[str]]):
    payload = {"nodes": nodes, "edges": edges}
    response = client.post("/api/graph/", json=payload)
    assert response.status_code == 201
    graph_id = response.json()["id"]

    response = client.get(f"/api/graph/{graph_id}/adjacency_list")
    assert response.status_code == status

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
def test_read_invalid_graph_adjacency_list(client: TestClient, path: str, expected_status: int):
    response = client.get(path)
    assert response.status_code == expected_status

@pytest.mark.parametrize(
    "nodes, edges, status, expected_adj",
    [
        (
                [{"name": "a"}, {"name": "b"}, {"name": "c"}],
                [{"source": "a", "target": "b"}, {"source": "b", "target": "c"}],
                200,
                {"a": [], "b": ["a"], "c": ["b"]}
        ),
        (
                [{"name": "a"}, {"name": "b"}, {"name": "c"}, {"name": "d"}],
                [{"source": "a", "target": "b"}, {"source": "a", "target": "c"}, {"source": "a", "target": "d"}],
                200,
                {"a": [], "b": ["a"], "c": ["a"], "d": ["a"]}
        ),
        (
                [{"name": "a"}, {"name": "b"}],
                [],
                200,
                {"a": [], "b": []}
        ),
    ]
)
def test_read_graph_reverse_adjacency_list(client: TestClient,
                                            nodes: list[dict[str, str]],
                                            edges: list[dict[str, str]],
                                            status: int,
                                            expected_adj: dict[str, list[str]]):
    payload = {"nodes": nodes, "edges": edges}
    response = client.post("/api/graph/", json=payload)
    assert response.status_code == 201
    graph_id = response.json()["id"]

    response = client.get(f"/api/graph/{graph_id}/reverse_adjacency_list")
    assert response.status_code == status

    data = response.json()
    assert "adjacency_list" in data
    assert data["adjacency_list"] == expected_adj