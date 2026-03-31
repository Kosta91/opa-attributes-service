"""JWT authentication dependency.

Currently operates in pass-through mode: any Bearer token is accepted
without signature or claims validation. Requests without a token are
rejected with 401.
"""

from __future__ import annotations

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

_scheme = HTTPBearer()


async def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(_scheme),
) -> str:
    """Validate that a Bearer token is present and return the raw token.

    Raises ``HTTPException(401)`` when the Authorization header is missing
    or does not use the Bearer scheme (handled by ``HTTPBearer``).
    """
    return credentials.credentials
