"""API layer — routers and exception handlers."""

from app.api.public import router as public_router
from app.api.exception_handler import register_exception_handlers