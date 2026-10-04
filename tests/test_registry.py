from fastapi.testclient import TestClient
from multimodel.main import app
from multimodel import registry

client = TestClient(app)


def setup_function():
    registry.CHAMPION = next(iter(registry.MODELS))


def test_promote():
    client.post("/models", json={"name": "fraud", "version": "2", "metrics": {"auc": 0.9}})
    payload = client.post("/promote", json={"name": "fraud"}).json()
    assert payload["champion"] == "fraud"
    assert payload["applied"] is False
    assert client.get("/champion").json()["champion"] == "fraud"
