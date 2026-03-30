"""External attribute sources (Azure Entra ID, etc.)."""

from app.external.base import ExternalAttributeSource, get_external_source
from app.external.entra_id import EntraIDAttributeSource
