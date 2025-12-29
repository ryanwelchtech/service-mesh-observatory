"""
Background Metrics Collector
Continuously collects metrics from Prometheus and broadcasts via WebSocket
"""

import asyncio
from datetime import datetime
import structlog
from typing import Dict, Any

from app.core.config import settings
from app.core.websocket import connection_manager
from app.services.prometheus_service import prometheus_service

logger = structlog.get_logger()


class MetricsCollector:
    """Background task for collecting and broadcasting metrics"""

    def __init__(self):
        self.is_running = False
        self._task = None

    async def start(self):
        """Start the metrics collection background task"""
        if self.is_running:
            logger.warning("Metrics collector already running")
            return

        self.is_running = True
        self._task = asyncio.create_task(self._collection_loop())
        logger.info("Metrics collector started")

    async def stop(self):
        """Stop the metrics collection background task"""
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Metrics collector stopped")

    async def _collection_loop(self):
        """Main collection loop"""
        while self.is_running:
            try:
                # Collect metrics from Prometheus
                metrics = await self._collect_metrics()

                # Broadcast to connected WebSocket clients
                if connection_manager.get_connection_count() > 0:
                    await connection_manager.broadcast_metrics_update(metrics)

                logger.debug(
                    "Metrics collected and broadcast",
                    connections=connection_manager.get_connection_count()
                )

            except Exception as e:
                logger.error("Error in metrics collection loop", error=str(e))

            # Wait for next collection interval
            await asyncio.sleep(settings.METRICS_COLLECTION_INTERVAL)

    async def _collect_metrics(self) -> Dict[str, Any]:
        """Collect current metrics from Prometheus"""
        try:
            overview = await prometheus_service.get_mesh_overview()

            return {
                "timestamp": datetime.utcnow().isoformat(),
                "request_rate": overview.get("request_rate", 0),
                "error_rate": overview.get("error_rate", 0),
                "p50_latency": overview.get("p50_latency", 0),
                "p95_latency": overview.get("p95_latency", 0),
                "p99_latency": overview.get("p99_latency", 0),
                "active_connections": overview.get("active_connections", 0)
            }
        except Exception as e:
            logger.error("Failed to collect metrics", error=str(e))
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }


# Global metrics collector instance
metrics_collector = MetricsCollector()
