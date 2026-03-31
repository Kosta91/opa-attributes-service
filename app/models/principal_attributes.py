"""ORM model for principal attributes (key-value pairs per principal)."""

from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.base import Base
from app.models.attribute_sources import AttributeSource


class PrincipalAttribute(Base):
    __tablename__ = "principal_attributes"
    
    principal_id: Mapped[String] = mapped_column(String(100), primary_key=True, index=True)
    attribute_key: Mapped[String] = mapped_column(String(100), primary_key=True)
    attribute_value: Mapped[String] = mapped_column(String(255), nullable=True)
    source_name: Mapped[String] = mapped_column(String(100), ForeignKey("attribute_sources.source_name"), nullable=False)
    last_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    source = Mapped[AttributeSource] = relationship("AttributeSource", back_populates="attributes")