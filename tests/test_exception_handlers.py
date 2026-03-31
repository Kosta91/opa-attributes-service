"""Tests for exception-to-HTTP-response mapping."""

from unittest.mock import AsyncMock, patch

from app.exceptions import (
    AttributeConflictError,
    DatabaseReadError,
    DatabaseWriteError,
    ExternalSourceAuthError,
    ExternalSourceRequestError,
    ExternalSourceResponseError,
    PrincipalNotFoundError,
)

AUTH_HEADER = {"Authorization": "Bearer test-token"}


def test_principal_not_found(app_client):
    """PrincipalNotFoundError → 404."""
    response = app_client.get("/attributes/unknown", headers=AUTH_HEADER)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_database_read_error(app_client):
    """DatabaseReadError → 500."""
    with patch(
        "app.core.opa.get_principal_attributes_from_db",
        new_callable=AsyncMock,
        side_effect=DatabaseReadError("test"),
    ):
        response = app_client.get("/attributes/alice", headers=AUTH_HEADER)
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"


def test_database_write_error(app_client):
    """DatabaseWriteError → 500."""
    with patch(
        "app.core.opa.add_principal_attributes_to_db",
        new_callable=AsyncMock,
        side_effect=DatabaseWriteError("test"),
    ):
        response = app_client.get("/attributes/alice", headers=AUTH_HEADER)
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"


def test_attribute_conflict_error(app_client):
    """AttributeConflictError → 409."""
    with patch(
        "app.core.opa.add_principal_attributes_to_db",
        new_callable=AsyncMock,
        side_effect=AttributeConflictError("alice"),
    ):
        response = app_client.get("/attributes/alice", headers=AUTH_HEADER)
    assert response.status_code == 409


def test_external_source_auth_error(app_client):
    """ExternalSourceAuthError → 502."""
    with patch(
        "app.api.public.get_principal_attributes",
        new_callable=AsyncMock,
        side_effect=ExternalSourceAuthError("entra_id", "bad creds"),
    ):
        response = app_client.get("/attributes/alice", headers=AUTH_HEADER)
    assert response.status_code == 502
    assert "authentication failed" in response.json()["detail"].lower()


def test_external_source_request_error(app_client):
    """ExternalSourceRequestError → 502."""
    with patch(
        "app.api.public.get_principal_attributes",
        new_callable=AsyncMock,
        side_effect=ExternalSourceRequestError("entra_id", "timeout"),
    ):
        response = app_client.get("/attributes/alice", headers=AUTH_HEADER)
    assert response.status_code == 502
    assert "unavailable" in response.json()["detail"].lower()


def test_external_source_response_error(app_client):
    """ExternalSourceResponseError → 502."""
    with patch(
        "app.api.public.get_principal_attributes",
        new_callable=AsyncMock,
        side_effect=ExternalSourceResponseError("entra_id", 503),
    ):
        response = app_client.get("/attributes/alice", headers=AUTH_HEADER)
    assert response.status_code == 502
    assert "unexpected response" in response.json()["detail"].lower()
