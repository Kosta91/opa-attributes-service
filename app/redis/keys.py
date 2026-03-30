"""Cache key builders for the application."""

from functools import lru_cache


@lru_cache(maxsize=100)
def principal_attrs_key(principal_id: str) -> str:
    return f"principal_attrs:{principal_id}"
