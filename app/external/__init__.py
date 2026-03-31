"""External attribute sources (Azure Entra ID, etc.)."""

from app.external.base import ExternalAttributeSource, get_external_sources
from app.external.entra_id import EntraIDAttributeSource
from app.external.registry import create_external_sources
