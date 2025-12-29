"""
WebSocket connection manager for real-time updates
Manages client connections and broadcasts service mesh events
"""

from fastapi import WebSocket
from typing import List, Dict, Any
import structlog
import json
from datetime import datetime

logger = structlog.get_logger()


class ConnectionManager:
    """Manages WebSocket connections and broadcasting"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket):
        """Accept and track new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_metadata[websocket] = {
            "connected_at": datetime.utcnow().isoformat(),
            "messages_sent": 0
        }
        logger.info(
            "WebSocket client connected",
            total_connections=len(self.active_connections)
        )

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            del self.connection_metadata[websocket]
            logger.info(
                "WebSocket client disconnected",
                total_connections=len(self.active_connections)
            )

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send message to specific client"""
        try:
            await websocket.send_json(message)
            self.connection_metadata[websocket]["messages_sent"] += 1
        except Exception as e:
            logger.error("Failed to send personal message", error=str(e))
            self.disconnect(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        disconnected = []
        message_json = json.dumps(message)

        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
                self.connection_metadata[connection]["messages_sent"] += 1
            except Exception as e:
                logger.error("Failed to broadcast to client", error=str(e))
                disconnected.append(connection)

        # Clean up failed connections
        for connection in disconnected:
            self.disconnect(connection)

        logger.debug(
            "Broadcast message sent",
            active_connections=len(self.active_connections),
            failed_connections=len(disconnected)
        )

    async def broadcast_topology_update(self, topology: Dict[str, Any]):
        """Broadcast service mesh topology update"""
        await self.broadcast({
            "type": "topology_update",
            "timestamp": datetime.utcnow().isoformat(),
            "data": topology
        })

    async def broadcast_metrics_update(self, metrics: Dict[str, Any]):
        """Broadcast metrics update"""
        await self.broadcast({
            "type": "metrics_update",
            "timestamp": datetime.utcnow().isoformat(),
            "data": metrics
        })

    async def broadcast_alert(self, alert: Dict[str, Any]):
        """Broadcast security or operational alert"""
        await self.broadcast({
            "type": "alert",
            "timestamp": datetime.utcnow().isoformat(),
            "severity": alert.get("severity", "info"),
            "data": alert
        })

    async def broadcast_cert_expiry_warning(self, cert_info: Dict[str, Any]):
        """Broadcast certificate expiration warning"""
        await self.broadcast({
            "type": "cert_expiry_warning",
            "timestamp": datetime.utcnow().isoformat(),
            "data": cert_info
        })

    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            "active_connections": len(self.active_connections),
            "total_messages_sent": sum(
                meta["messages_sent"] for meta in self.connection_metadata.values()
            )
        }


# Global connection manager instance
connection_manager = ConnectionManager()
