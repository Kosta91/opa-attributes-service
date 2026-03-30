from __future__ import annotations

import logging

import httpx
import msal

from app.external.base import ExternalAttributeSource
from app.external.settings import entra_id_settings

logger = logging.getLogger(__name__)

GRAPH_USER_URL = "https://graph.microsoft.com/v1.0/users/{principal_id}"


class EntraIDAttributeSource(ExternalAttributeSource):
    """Fetches user attributes from Azure Entra ID via Microsoft Graph API."""

    def __init__(self) -> None:
        self._msal_app = msal.ConfidentialClientApplication(
            client_id=entra_id_settings.ENTRA_CLIENT_ID,
            client_credential=entra_id_settings.ENTRA_CLIENT_SECRET,
            authority=entra_id_settings.authority,
        )


    def _acquire_token(self) -> str:
        result = self._msal_app.acquire_token_for_client(
            scopes=entra_id_settings.ENTRA_SCOPES,
        )
        if "access_token" not in result:
            error = result.get("error_description", "unknown error")
            raise RuntimeError(f"Failed to acquire Entra ID token: {error}")
        return result["access_token"]


    async def fetch_attributes(self, principal_id: str) -> dict[str, str] | None:
        """Fetch user attributes from Microsoft Graph API."""
        try:
            token = self._acquire_token()
        except RuntimeError:
            logger.exception("Entra ID token acquisition failed for principal_id=%s", principal_id)
            # TODO: raise custom service error instead
            return None

        url = GRAPH_USER_URL.format(principal_id=principal_id)
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers={"Authorization": f"Bearer {token}"},
                )
        except httpx.HTTPError:
            logger.exception("Graph API request failed for principal_id=%s", principal_id)
            # TODO: raise custom service error instead
            return None

        if response.status_code == 404:
            return None

        if response.status_code != 200:
            logger.error(
                "Graph API returned %d for principal_id=%s: %s",
                response.status_code, principal_id, response.text,
            )
            # TODO: raise custom service error instead
            return None

        data = response.json()
        return {
            k: str(v)
            for k, v in data.items()
            if v is not None and not k.startswith("@")
        }
