"""
WebSocket endpoints for real-time updates
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from apps.api.app.websockets.manager import manager
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(None)):
    """
    WebSocket endpoint for real-time updates

    Usage:
    ```
    const ws = new WebSocket('ws://localhost:8000/ws?token=YOUR_TOKEN');
    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      console.log(data);
    };
    ```
    """
    # Note: In production, validate token properly
    # For now, accept all connections with tenant_id = 1
    tenant_id = 1

    try:
        await manager.connect(websocket, tenant_id)
        logger.info(f"WebSocket client connected for tenant {tenant_id}")

        while True:
            # Receive data from client
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_json(
                    {
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

            # Echo back (for testing)
            elif message.get("type") == "test":
                await websocket.send_json(
                    {
                        "type": "test_response",
                        "payload": message.get("payload"),
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

            else:
                logger.debug(f"Received message type: {message.get('type')}")

    except WebSocketDisconnect:
        manager.disconnect(websocket, tenant_id)
        logger.info(f"Client disconnected from tenant {tenant_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, tenant_id)
