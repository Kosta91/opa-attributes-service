"""API integration tests using FastAPI TestClient."""

AUTH_HEADER = {"Authorization": "Bearer test-token"}


def test_root(app_client):
    """GET / returns the service identifier."""
    response = app_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"service": "prodsec.opa_attribute_storage"}


def test_health(app_client):
    """GET /health returns ok."""
    response = app_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_get_attributes_no_token(app_client):
    """GET /attributes/alice without Bearer token returns 401."""
    response = app_client.get("/attributes/alice")
    assert response.status_code == 401


def test_get_attributes_with_token(app_client):
    """GET /attributes/alice with Bearer token returns aggregated attributes."""
    response = app_client.get("/attributes/alice", headers=AUTH_HEADER)
    assert response.status_code == 200

    data = response.json()
    assert data["principal_id"] == "alice"
    attrs = data["attributes"]
    # identity attrs
    assert attrs["email"] == "alice@example.com"
    assert attrs["name"] == "Alice Johnson"
    # org attrs
    assert attrs["department"] == "Vehicle Security"
    assert attrs["team"] == "VehicleSec"


def test_get_attributes_unknown_principal(app_client):
    """GET /attributes/unknown with token returns 404."""
    response = app_client.get("/attributes/unknown", headers=AUTH_HEADER)
    assert response.status_code == 404
