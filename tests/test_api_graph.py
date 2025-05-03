from starlette.testclient import TestClient


def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_and_get_graph(client: TestClient):
    payload = {"nodes": [{"name": "a"}, {"name": "b"}], "edges": [{"source": "a", "target": "b"}]}
    response = client.post("/api/graph", json=payload)
    assert response.status_code == 201
    graph_id = response.json()["id"]

    response = client.get(f"/api/graph/{graph_id}/")
    assert response.status_code == 200
    data = response.json()
    assert data["nodes"] == payload["nodes"]
    assert data["edges"] == payload["edges"]


def test_create_invalid_graph(client: TestClient):
    payloads = [
        # non-existent nodes
        {"nodes": [{"name": "a"}, {"name": "b"}], "edges": [{"source": "c", "target": "d"}]},
        {"nodes": [{"name": "a"}, {"name": "b"}], "edges": [{"source": "a", "target": "c"}]},
        # no nodes
        {"nodes": [], "edges": []},
        {"nodes": [], "edges": [{"source": "a", "target": "b"}]},
        # node name contains extraneous characters
        {"nodes": [{"name": "a1"}, {"name": "b1"}], "edges": [{"source": "a1", "target": "b1"}]},
        {"nodes": [{"name": "a_a"}, {"name": "b_b"}], "edges": [{"source": "a_a", "target": "b_b"}]},
        # names of nodes are not unique
        {"nodes": [{"name": "a"}, {"name": "a"}, {"name": "b"}], "edges": [{"source": "a", "target": "b"}]},
        # more than one edge between vertices
        {"nodes": [{"name": "a"}, {"name": "b"}], "edges": [{"source": "a", "target": "b"}, {"source": "a", "target": "b"}]},
        # incorrect number of characters in node name
        {"nodes": [{"name": ""}, {"name": "b"}], "edges": [{"source": "", "target": "b"}]},
        {"nodes": [{"name": "a" * 256}, {"name": "b"}], "edges": [{"source": "a" * 256, "target": "b"}]},
    ]
    for payload in payloads:
        response = client.post("/api/graph", json=payload)
        assert response.status_code == 400

    payloads = [
        {"nodes": [{"name": 1}, {"name": "b"}], "edges": [{"source": 1, "target": "b"}]},
        {"vertexes": [{"name": "a"}, {"name": "b"}], "edges": [{"source": "a", "target": "b"}]},
    ]
    for payload in payloads:
        response = client.post("/api/graph", json=payload)
        assert response.status_code == 422

def test_get_invalid_graph(client: TestClient):
    response = client.get("/api/graph/100")
    assert response.status_code == 404

    response = client.get("/api/graph/invalid")
    assert response.status_code == 422