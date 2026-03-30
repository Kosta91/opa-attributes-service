"""Domain exceptions for OPA-attributes-service (framework-agnostic)."""


class OPAAttributesServiceError(Exception):
    """Base exception for OPA attribute service errors."""


# --- Principal / lookup ---

class PrincipalNotFoundError(OPAAttributesServiceError):
    """Principal was not found in any source (cache, DB, external)."""

    def __init__(self, principal_id: str) -> None:
        self.principal_id = principal_id
        super().__init__(f"Principal not found: {principal_id}")


# --- Database ---

class DatabaseReadError(OPAAttributesServiceError):
    """Failed to read from the database."""

    def __init__(self, detail: str = "Database read operation failed") -> None:
        super().__init__(detail)


class DatabaseWriteError(OPAAttributesServiceError):
    """Failed to write to the database."""

    def __init__(self, detail: str = "Database write operation failed") -> None:
        super().__init__(detail)


class AttributeConflictError(OPAAttributesServiceError):
    """Attributes already exist for the given principal (integrity constraint)."""

    def __init__(self, principal_id: str) -> None:
        self.principal_id = principal_id
        super().__init__(f"Attributes already exist for principal: {principal_id}")


# --- External source ---

class ExternalSourceAuthError(OPAAttributesServiceError):
    """Failed to authenticate with an external attribute source."""

    def __init__(self, source: str, detail: str = "") -> None:
        self.source = source
        msg = f"Authentication failed for external source: {source}"
        if detail:
            msg = f"{msg} — {detail}"
        super().__init__(msg)


class ExternalSourceRequestError(OPAAttributesServiceError):
    """Request to an external attribute source failed."""

    def __init__(self, source: str, detail: str = "") -> None:
        self.source = source
        msg = f"Request failed for external source: {source}"
        if detail:
            msg = f"{msg} — {detail}"
        super().__init__(msg)


class ExternalSourceResponseError(OPAAttributesServiceError):
    """External attribute source returned an unexpected response."""

    def __init__(self, source: str, status_code: int) -> None:
        self.source = source
        self.status_code = status_code
        super().__init__(f"External source {source} returned unexpected status {status_code}")
