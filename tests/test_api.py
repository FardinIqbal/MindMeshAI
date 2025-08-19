from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_rebuttal():
    response = client.post("/api/rebuttal", json={"claim": "Cats are great"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["rebuttals"]) == 3
    assert all("citations" in r for r in data["rebuttals"])


def test_tree_and_audit():
    # Generate a tree with an absolute term to trigger audit issue
    response = client.post("/api/tree/generate", json={"topic": "Cats always win"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["children"]) == 3
    tree_id = data["id"]

    audit_resp = client.post("/api/audit", json={"tree_id": tree_id})
    assert audit_resp.status_code == 200
    issues = audit_resp.json()["issues"]
    assert len(issues) >= 1


def test_lens():
    response = client.post(
        "/api/lens", json={"claim": "Test", "lens": ["Utilitarian"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["perspectives"][0]["lens"] == "Utilitarian"


def test_research():
    response = client.post("/api/research", json={"query": "Cats"})
    assert response.status_code == 200
    data = response.json()
    assert data["citations"][0]["url"].startswith("https://")
