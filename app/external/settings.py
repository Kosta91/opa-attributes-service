"""Azure Entra ID settings loaded from environment variables."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EntraIDSettings(BaseSettings):
    """Azure Entra ID configuration for Microsoft Graph API access."""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    ENTRA_TENANT_ID: str = Field(description="Azure AD tenant ID")
    ENTRA_CLIENT_ID: str = Field(description="Application (client) ID")
    ENTRA_CLIENT_SECRET: str = Field(description="Client secret")
    ENTRA_AUTHORITY: str = Field(
        default="",
        description="MSAL authority URL. Built from tenant ID if not set.",
    )
    ENTRA_SCOPES: list[str] = Field(
        default=["https://graph.microsoft.com/.default"],
        description="OAuth2 scopes for client credentials flow.",
    )

    @property
    def authority(self) -> str:
        if self.ENTRA_AUTHORITY:
            return self.ENTRA_AUTHORITY
        return f"https://login.microsoftonline.com/{self.ENTRA_TENANT_ID}"


entra_id_settings = EntraIDSettings()
