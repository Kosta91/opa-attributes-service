"""Standalone worker that periodically syncs principal attributes from external sources into the DB."""

from __future__ import annotations

import asyncio
import logging

from app.crud import (
    get_principal_ids_by_source,
    get_principal_attributes_by_source,
    upsert_principal_attributes,
    delete_principal_attributes_by_source,
    update_source_sync_status,
)
from app.db.base import AsyncSessionLocal
from app.external.base import ExternalAttributeSource
from app.sync.settings import sync_settings

logger = logging.getLogger("sync.worker")


class SyncWorker:
    """Periodically re-fetches attributes from external sources and updates the DB."""

    def __init__(
        self,
        externals: list[ExternalAttributeSource],
    ) -> None:
        """Initialize the sync worker with a list of external attribute sources."""
        self._externals = {src.source_name: src for src in externals}
        self._task: asyncio.Task | None = None

    def start(self) -> None:
        """Start the periodic sync loop as a background asyncio task."""
        if not sync_settings.SYNC_ENABLED:
            logger.info("Sync worker is disabled")
            return
        self._task = asyncio.create_task(self._run_loop())
        logger.info(
            "Sync worker started (interval=%ds, batch_size=%d, sources=%s)",
            sync_settings.SYNC_INTERVAL_SECONDS,
            sync_settings.SYNC_BATCH_SIZE,
            list(self._externals.keys()),
        )

    async def stop(self) -> None:
        """Cancel the background task and wait for it to finish."""
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            logger.info("Sync worker stopped")

    async def run(self) -> None:
        """Run the sync loop as a standalone process (blocking). Handles graceful shutdown on SIGINT/SIGTERM."""
        import signal

        loop = asyncio.get_running_loop()
        stop_event = asyncio.Event()

        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, stop_event.set)

        logger.info(
            "Sync worker running in standalone mode (interval=%ds, batch_size=%d, sources=%s)",
            sync_settings.SYNC_INTERVAL_SECONDS,
            sync_settings.SYNC_BATCH_SIZE,
            list(self._externals.keys()),
        )

        while not stop_event.is_set():
            try:
                await self._sync_all_sources()
            except Exception:
                logger.exception("Sync cycle failed unexpectedly")

            try:
                await asyncio.wait_for(stop_event.wait(), timeout=sync_settings.SYNC_INTERVAL_SECONDS)
            except asyncio.TimeoutError:
                pass

        logger.info("Sync worker stopped")

    async def _run_loop(self) -> None:
        """Sleep -> sync -> repeat. Errors are logged but never stop the loop."""
        while True:
            await asyncio.sleep(sync_settings.SYNC_INTERVAL_SECONDS)
            try:
                await self._sync_all_sources()
            except Exception:
                logger.exception("Sync cycle failed unexpectedly")

    async def _sync_all_sources(self) -> None:
        """Iterate over registered external sources and sync each one."""
        for source_name, external in self._externals.items():
            try:
                await self._sync_source(source_name, external)
            except Exception:
                logger.exception("Failed to sync source=%s", source_name)
                async with AsyncSessionLocal() as db:
                    await update_source_sync_status(db, source_name, "error")

    async def _sync_source(self, source_name: str, external: ExternalAttributeSource) -> None:
        """Re-fetch attributes for every principal linked to the given source."""
        logger.info("Starting sync for source=%s", source_name)

        async with AsyncSessionLocal() as db:
            await update_source_sync_status(db, source_name, "syncing")
            principal_ids = await get_principal_ids_by_source(db, source_name)

        synced = 0
        for i in range(0, len(principal_ids), sync_settings.SYNC_BATCH_SIZE):
            batch = principal_ids[i : i + sync_settings.SYNC_BATCH_SIZE]
            for pid in batch:
                try:
                    await self._sync_principal(pid, source_name, external)
                    synced += 1
                except Exception:
                    logger.exception("Failed to sync principal=%s from source=%s", pid, source_name)

        async with AsyncSessionLocal() as db:
            await update_source_sync_status(db, source_name, "ok")
        logger.info("Sync complete for source=%s: %d/%d principals synced", source_name, synced, len(principal_ids))

    async def _sync_principal(
        self, principal_id: str, source_name: str, external: ExternalAttributeSource,
    ) -> None:
        """Fetch fresh attributes for one principal and update the DB if changed."""
        fresh_attrs = await external.fetch_attributes(principal_id)

        async with AsyncSessionLocal() as db:
            if fresh_attrs is None:
                await delete_principal_attributes_by_source(db, principal_id, source_name)
                return

            existing = await get_principal_attributes_by_source(db, principal_id, source_name)

            if existing == fresh_attrs:
                return

            await upsert_principal_attributes(db, principal_id, source_name, fresh_attrs)
