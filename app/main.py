"""OPA Attributes Service — FastAPI application entry point."""

from app.app import app

import uvicorn


if __name__ == "__main__":
    uvicorn.run(app)
