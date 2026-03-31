"""OPA Attributes Service — application entry point.

Supports two run modes:
  - ``serve`` (default): start the FastAPI HTTP server.
  - ``sync``: run the background sync worker as a standalone process.

Usage::

    python -m app serve          # HTTP server
    python -m app sync           # standalone sync worker
"""

import argparse
import asyncio
import logging
import sys

import uvicorn

from app.external import EntraIDAttributeSource
from app.sync import SyncWorker

logger = logging.getLogger(__name__)


def _build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(description="OPA Attributes Service")
    subparsers = parser.add_subparsers(dest="mode", help="Run mode")

    subparsers.add_parser("serve", help="Start the FastAPI HTTP server (default)")
    subparsers.add_parser("sync", help="Run the sync worker as a standalone process")

    return parser


def _run_serve() -> None:
    """Start the FastAPI HTTP server."""
    from app.app import app  # noqa: delayed import to avoid circular deps

    uvicorn.run(app)


async def _run_sync() -> None:
    """Initialize dependencies and run the sync worker loop."""
    external = EntraIDAttributeSource()
    worker = SyncWorker(external=external)
    await worker.run()


def main() -> None:
    """Parse CLI arguments and dispatch to the selected run mode."""
    parser = _build_parser()
    args = parser.parse_args()

    mode = args.mode or "serve"

    if mode == "serve":
        _run_serve()
    elif mode == "sync":
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
        asyncio.run(_run_sync())
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
