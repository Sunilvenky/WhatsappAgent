"""WhatsApp webhook endpoints for receiving incoming messages."""

from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from apps.api.app.core.database import get_db
from apps.api.app.core.config import settings
from apps.api.app.crud import conversation_crud, message_crud
from apps.api.app.models.message import MessageDirection
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class IncomingMessage(BaseModel):
    """Schema for incoming WhatsApp message."""
    id: str
    from_: str = None
    timestamp: int
    message: str
    type: str
    sessionId: str
    
    class Config:
        populate_by_name = True
        fields = {'from_': 'from'}


class MessageStatusUpdate(BaseModel):
    """Schema for message status updates."""
    event: str
    messageId: str
    status: str
    sessionId: str


def verify_webhook_secret(x_webhook_secret: Optional[str] = Header(None)):
    """Verify webhook secret for security."""
    if not x_webhook_secret or x_webhook_secret != settings.WHATSAPP_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook secret"
        )
    return True


@router.post("/whatsapp/incoming")
async def receive_whatsapp_message(
    payload: dict,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_webhook_secret)
):
    """
    Webhook endpoint to receive incoming WhatsApp messages.
    Called by WhatsApp Gateway when messages are received.
    """
    try:
        # Check if it's a message status update or incoming message
        if payload.get('event') == 'message_status':
            return await handle_message_status_update(payload, db)
        
        # Parse incoming message
        try:
            incoming = IncomingMessage(**payload)
        except Exception as e:
            logger.error(f"Failed to parse incoming message: {e}")
            return {"status": "error", "message": "Invalid payload"}
        
        # Extract phone number from WhatsApp JID
        phone_number = incoming.from_.split('@')[0] if incoming.from_ else None
        
        if not phone_number:
            logger.warning("No phone number in incoming message")
            return {"status": "error", "message": "No phone number"}
        
        logger.info(f"Received message from {phone_number}: {incoming.message}")
        
        # Process message asynchronously using Celery worker
        from apps.api.app.workers.message_worker import process_incoming_message
        
        process_incoming_message.delay(
            from_phone=phone_number,
            message_text=incoming.message,
            external_id=incoming.id,
            metadata={
                "timestamp": incoming.timestamp,
                "type": incoming.type,
                "session_id": incoming.sessionId,
                "raw_payload": payload
            }
        )
        
        logger.info(f"Queued message processing for: {incoming.id}")
        
        return {
            "status": "success",
            "messageId": incoming.id,
            "message": "Message received and processed"
        }
        
    except Exception as e:
        logger.error(f"Error processing incoming message: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


async def handle_message_status_update(payload: dict, db: Session):
    """Handle message status updates (delivered, read, etc.)."""
    try:
        update = MessageStatusUpdate(**payload)
        
        logger.info(f"Message status update: {update.messageId} -> {update.status}")
        
        # Update message status asynchronously using Celery worker
        from apps.api.app.workers.message_worker import update_message_status
        
        # Find message by external ID
        message = message_crud.get_message_by_external_id(db, update.messageId)
        if message:
            update_message_status.delay(
                message_id=message.id,
                status=update.status,
                metadata={"session_id": update.sessionId, "raw_payload": payload}
            )
        
        return {
            "status": "success",
            "message": "Status update processed"
        }
        
    except Exception as e:
        logger.error(f"Error processing status update: {e}")
        return {
            "status": "error",
            "message": str(e)
        }


@router.get("/whatsapp/test")
async def test_webhook():
    """Test endpoint to verify webhook is working."""
    return {
        "status": "ok",
        "message": "WhatsApp webhook is active",
        "timestamp": "2025-10-23T00:00:00Z"
    }
