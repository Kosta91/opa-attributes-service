"""ORM model for attribute sources (providers of principal attributes)."""

from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AttributeSource(Base):
    __tablename__ = "attribute_sources"

    source_name: Mapped[str] = mapped_column(String(255), primary_key=True)
    last_sync: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    sync_status: Mapped[String] = mapped_column(String(50), nullable=True)