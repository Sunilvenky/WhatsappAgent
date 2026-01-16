"""
WebSocket Connection Manager for Real-time Updates
"""
from typing import Set, Dict
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        # Store active WebSocket connections per tenant
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, tenant_id: int):
        """Connect a new client"""
        await websocket.accept()
        if tenant_id not in self.active_connections:
            self.active_connections[tenant_id] = set()
        self.active_connections[tenant_id].add(websocket)
        logger.info(
            f"✅ Client connected. Tenant {tenant_id}: {len(self.active_connections.get(tenant_id, []))} clients"
        )

    def disconnect(self, websocket: WebSocket, tenant_id: int):
        """Disconnect a client"""
        if tenant_id in self.active_connections:
            self.active_connections[tenant_id].discard(websocket)
            logger.info(
                f"❌ Client disconnected. Tenant {tenant_id}: {len(self.active_connections.get(tenant_id, []))} clients"
            )

    async def broadcast_to_tenant(self, tenant_id: int, message: dict):
        """Send message to all clients in a tenant"""
        if tenant_id not in self.active_connections:
            return

        disconnected = set()
        for connection in self.active_connections[tenant_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                disconnected.add(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection, tenant_id)

    async def broadcast_to_all(self, message: dict):
        """Send message to all connected clients"""
        for tenant_id in self.active_connections:
            await self.broadcast_to_tenant(tenant_id, message)


manager = ConnectionManager()
