# OPA Attributes Service

A FastAPI microservice that provides principal (user) attributes for [Open Policy Agent](https://www.openpolicyagent.org/) authorization decisions. Acts as a caching proxy between OPA and external identity providers (Azure Entra ID, etc.).

## Architecture

```
OPA  -->  GET /attributes/{principal_id}  -->  Cache  -->  Database  -->  External Sources
```

The service resolves attributes through a three-tier pipeline:

1. **Cache** (Redis or in-memory LRU) — fastest path, sub-millisecond.
2. **Database** (PostgreSQL) — persistent storage, populated by the sync worker or on first request.
3. **External sources** (Azure Entra ID, mock, etc.) — queried only on cache + DB miss. Results are persisted to DB and cached for subsequent requests.

The service runs in two modes from a single codebase:

- **`serve`** — HTTP API server (FastAPI + Uvicorn).
- **`sync`** — Standalone background worker that periodically re-fetches attributes from external sources and updates the database.

## API Endpoints

All `/attributes/*` endpoints require a `Bearer` token in the `Authorization` header. Health and root endpoints are unauthenticated.

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/` | No | Service identifier |
| `GET` | `/health` | No | Health check (returns `{"status": "ok"}`) |
| `GET` | `/ready` | No | Readiness probe (checks DB and Redis connectivity) |
| `GET` | `/attributes/{principal_id}` | Bearer | Returns aggregated attributes for a principal |

### GET /attributes/{principal_id}

**Request:**
```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/attributes/alice
```

**Response (200):**
```json
{
  "principal_id": "alice",
  "attributes": {
    "email": "alice@example.com",
    "name": "Alice Johnson",
    "department": "Vehicle Security",
    "team": "VehicleSec",
    "location": "Foster City",
    "oncall": "false",
    "jobTitle": "Security Engineer"
  }
}
```

**Error responses:**
| Status | Condition |
|--------|-----------|
| 401 | Missing or invalid Authorization header |
| 404 | Principal not found in any source |
| 409 | Attribute conflict (integrity constraint) |
| 500 | Database error |
| 502 | External source auth/request/response failure |

## Configuration

All settings are loaded from environment variables (or a `.env` file). Copy `.env.example` to `.env` to get started.

### Database

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | — | PostgreSQL connection string (`postgresql+asyncpg://...`) |
| `DB_POOL_SIZE` | `10` | Connection pool size |
| `DB_MAX_OVERFLOW` | `20` | Max overflow connections |
| `DB_POOL_TIMEOUT` | `10` | Pool checkout timeout (seconds) |
| `DB_POOL_RECYCLE` | `1800` | Connection recycle interval (seconds) |
| `DEBUG_SQL` | `false` | Echo SQL statements to logs |

### Redis (optional)

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_ENABLED` | `true` | Enable Redis cache. When `false`, uses in-memory LRU cache. |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |
| `REDIS_CACHE_TTL` | `3600` | Cache entry TTL in seconds |

### External Sources

| Variable | Default | Description |
|----------|---------|-------------|
| `MOCK_ENABLED` | `false` | Use mock external sources (for local development) |
| `EXTERNAL_SOURCES` | `["entra_id"]` | List of active external source names |

### Azure Entra ID

Required when `entra_id` is in `EXTERNAL_SOURCES` and `MOCK_ENABLED=false`.

| Variable | Default | Description |
|----------|---------|-------------|
| `ENTRA_TENANT_ID` | — | Azure AD tenant ID |
| `ENTRA_CLIENT_ID` | — | Application (client) ID |
| `ENTRA_CLIENT_SECRET` | — | Client secret |
| `ENTRA_AUTHORITY` | Auto from tenant ID | MSAL authority URL |
| `ENTRA_SCOPES` | `["https://graph.microsoft.com/.default"]` | OAuth2 scopes |

### Sync Worker

| Variable | Default | Description |
|----------|---------|-------------|
| `SYNC_ENABLED` | `true` | Enable the sync worker loop |
| `SYNC_INTERVAL_SECONDS` | `1800` | Interval between sync cycles (seconds) |
| `SYNC_BATCH_SIZE` | `50` | Number of principals to process per batch |

## Running

### Docker Compose (recommended)

```bash
cp .env.example .env
# Edit .env as needed

docker-compose up --build
```

This starts three containers:
- **postgres** — PostgreSQL 16
- **serve** — FastAPI HTTP server on port 8000
- **sync** — Background sync worker

Tables are created automatically on startup via `CREATE TABLE IF NOT EXISTS`.

### Local Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Set MOCK_ENABLED=true for local dev without Entra ID credentials

# Start the API server
python -m app serve

# Start the sync worker (separate terminal)
python -m app sync
```

### Mock Mode

Set `MOCK_ENABLED=true` in `.env` to use built-in mock external sources with sample data. This replaces real external sources with:
- **mock_identity** — returns email, name, oncall
- **mock_org** — returns department, jobTitle, team, location

No Entra ID credentials are required in mock mode.

## Adding a New External Source

1. Create a new class implementing `ExternalAttributeSource` (see `app/external/base.py`):
   - Implement the `source_name` property (unique string identifier).
   - Implement `async fetch_attributes(principal_id) -> dict[str, str] | None`.
2. Register it in `app/external/registry.py` (`_REGISTRY` dict).
3. Add the source name to `EXTERNAL_SOURCES` in `.env`.

The source will be auto-registered in the `attribute_sources` database table on startup.

## Testing

```bash
pip install -r requirements.txt   # includes test dependencies
python -m pytest tests/ -v
```

Tests use an in-memory SQLite database and mock external sources. No running PostgreSQL or Redis instance is required.

## Project Structure

```
app/
  __main__.py          # Entry point (python -m app serve|sync)
  app.py               # FastAPI application setup and lifespan
  exceptions.py        # Domain exceptions
  api/
    auth.py            # JWT Bearer authentication dependency
    public.py          # API routes (/attributes/...)
    exception_handler.py  # Exception-to-HTTP mapping
  cache/
    base.py            # AbstractCache interface
    local_cache.py     # In-memory LRU implementation
    redis_cache.py     # Redis implementation
    keys.py            # Cache key builders
  core/
    opa.py             # Attribute resolution pipeline
  crud/
    opa.py             # DB operations for API layer
    sync.py            # DB operations for sync worker
  db/
    base.py            # SQLAlchemy engine and session factory
    db_settings.py     # Database settings
  external/
    base.py            # ExternalAttributeSource interface
    entra_id.py        # Azure Entra ID implementation
    registry.py        # Source factory and DB registration
    settings.py        # External source settings
    mock/
      mock_data.py     # Sample data for mock sources
      identity.py      # MockIdentitySource
      org.py           # MockOrgSource
  models/
    attribute_sources.py    # AttributeSource ORM model
    principal_attributes.py # PrincipalAttribute ORM model
  sync/
    worker.py          # Standalone sync worker
    settings.py        # Sync settings
tests/
  conftest.py          # Shared fixtures (DB, cache, TestClient)
  test_api.py          # API integration tests
  test_cache.py        # Cache unit tests
  test_core.py         # Resolution pipeline unit tests
  test_exception_handlers.py  # Error mapping tests
  test_external_mock.py       # Mock source tests
  test_sync_worker.py         # Sync worker tests
```
