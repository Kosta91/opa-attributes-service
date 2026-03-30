"""Azure Entra ID implementation of ExternalAttributeSource via Microsoft Graph API."""

from __future__ import annotations

import logging

import httpx
import msal

from app.exceptions import ExternalSourceAuthError, ExternalSourceRequestError, ExternalSourceResponseError
from app.external.base import ExternalAttributeSource
from app.external.settings import entra_id_settings

logger = logging.getLogger(__name__)

GRAPH_USER_URL = "https://graph.microsoft.com/v1.0/users/{principal_id}"
SOURCE_NAME = "entra_id"


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
            raise ExternalSourceAuthError(SOURCE_NAME, error)
        return result["access_token"]


    async def fetch_attributes(self, principal_id: str) -> dict[str, str] | None:
        """Fetch user attributes from Microsoft Graph API."""
        token = self._acquire_token()

        url = GRAPH_USER_URL.format(principal_id=principal_id)
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers={"Authorization": f"Bearer {token}"},
                )
        except httpx.HTTPError as exc:
            raise ExternalSourceRequestError(SOURCE_NAME, str(exc)) from exc

        if response.status_code == 404:
            return None

        if response.status_code != 200:
            raise ExternalSourceResponseError(SOURCE_NAME, response.status_code)

        data = response.json()
        return {
            k: str(v)
            for k, v in data.items()
            if v is not None and not k.startswith("@")
        }
