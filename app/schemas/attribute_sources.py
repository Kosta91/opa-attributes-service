from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class AttributeSourceOutput(BaseModel):
    """Represents an attribute source as returned by the API."""

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
    )

    source_name: str = Field(..., description="Unique name of the attribute source")
    last_sync: Optional[datetime] = Field(None, description="Timestamp of the last synchronization")
    sync_status: Optional[str] = Field(None, description="Current synchronization status")