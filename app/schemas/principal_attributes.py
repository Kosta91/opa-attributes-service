from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class PrincipalAttributeOutput(BaseModel):
    """Represents a principal attribute as returned by the API."""

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
    )

    principal_id: str = Field(..., description="Unique identifier for the principal")
    attribute_key: str = Field(..., description="Key of the principal attribute")
    attribute_value: Optional[str] = Field(None, description="Value of the principal attribute")
    source_id: Optional[str] = Field(None, description="Identifier of the source that provided this attribute")
    last_updated: Optional[datetime] = Field(None, description="Timestamp of when this attribute was last updated")