import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    "path,status,body",
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
    "payload",
    [
        {"nodes": [{"name": "a"}, {"name": "b"}], "edges": [{"source": "a", "target": "b"}]},
    ], ids=[
        "simple-graph"
    ]
)
def test_create_and_get_graph(client: TestClient, payload):
    post = client.post("/api/graph/", json=payload)
    assert post.status_code == 201
    graph_id = post.json()["id"]

    get = client.get(f"/api/graph/{graph_id}/")
    assert get.status_code == 200
    data = get.json()
    assert data["nodes"] == payload["nodes"]
    assert data["edges"] == payload["edges"]


@pytest.mark.parametrize(
    "payload, expected_status",
    [
        ({"nodes": [{"name": "a"}, {"name": "b"}], "edges": [{"source": "c", "target": "d"}]}, 400),
        ({"nodes": [{"name": "a"}, {"name": "b"}], "edges": [{"source": "a", "target": "c"}]}, 400),
        ({"nodes": [], "edges": []}, 400),
        ({"nodes": [], "edges": [{"source": "a", "target": "b"}]}, 400),
        ({"nodes": [{"name": "a1"}, {"name": "b1"}], "edges": [{"source": "a1", "target": "b1"}]}, 400),
        ({"nodes": [{"name": "a_a"}, {"name": "b_b"}], "edges": [{"source": "a_a", "target": "b_b"}]}, 400),
        ({"nodes": [{"name": "a"}, {"name": "a"}, {"name": "b"}], "edges": [{"source": "a", "target": "b"}]}, 400),
        ({"nodes": [{"name": "a"}, {"name": "b"}],
          "edges": [{"source": "a", "target": "b"}, {"source": "a", "target": "b"}]}, 400),
        ({"nodes": [{"name": ""}, {"name": "b"}], "edges": [{"source": "", "target": "b"}]}, 400),
        ({"nodes": [{"name": "a" * 256}, {"name": "b"}], "edges": [{"source": "a" * 256, "target": "b"}]}, 400),

        ({"nodes": [{"name": 1}, {"name": "b"}], "edges": [{"source": 1, "target": "b"}]}, 422),
        ({"vertexes": [{"name": "a"}, {"name": "b"}], "edges": [{"source": "a", "target": "b"}]}, 422),
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
        "wrong-type-in-node",
        "wrong-key-nodes",
    ]
)
def test_create_invalid_graph(client: TestClient, payload, expected_status):
    response = client.post("/api/graph/", json=payload)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "path, expected_status",
    [
        ("/api/graph/100/", 404),
        ("/api/graph/invalid/", 422),
    ], ids=[
        "not-found-id", "invalid-id-format"
    ]
)
def test_get_invalid_graph(client: TestClient, path, expected_status):
    response = client.get(path)
    assert response.status_code == expected_status
