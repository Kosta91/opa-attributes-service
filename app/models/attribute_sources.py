"""ORM model for attribute sources (providers of principal attributes)."""

from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.base import Base


class AttributeSource(Base):
    __tablename__ = "attribute_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_id: Mapped[String] = mapped_column(String(100), primary_key=True)
    source_name: Mapped[String] = mapped_column(String(255), nullable=False)
    last_sync: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    sync_status: Mapped[String] = mapped_column(String(50), nullable=True)