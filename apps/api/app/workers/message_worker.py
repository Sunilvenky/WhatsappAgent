"""
Message processing workers.
"""
import logging
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from .celery_app import celery_app
from ..core.database import get_db
from ..crud import message as message_crud
from ..crud import conversation as conversation_crud
from ..models.message import MessageStatus
from ..connectors.whatsapp_gateway import WhatsAppGatewayConnector
from ..ai import ReplyClassifier
from ..core.config import settings
from .utils import RetryManager

logger = logging.getLogger(__name__)


@celery_app.task(name="app.workers.message_worker.send_message")
def send_message(message_id: int):
    """
    Send a single message.
    
    Args:
        message_id: Message ID to send
    """
    asyncio.run(_send_message_async(message_id))


async def _send_message_async(message_id: int):
    """Async message sending."""
    db = next(get_db())
    
    try:
        message = message_crud.get_message(db, message_id)
        if not message:
            logger.error(f"Message {message_id} not found")
            return
        
        if message.status == MessageStatus.SENT:
            logger.warning(f"Message {message_id} already sent")
            return
        
        # Send via gateway
        gateway = WhatsAppGatewayConnector()
        result = await gateway.send_message(
            to=message.contact.phone,
            message=message.content
        )
        
        # Update message
        if result.get("success"):
            message_crud.update_message(
                db,
                message_id,
                {
                    "status": MessageStatus.SENT,
                    "external_id": result.get("message_id"),
                    "sent_at": datetime.utcnow(),
                    "metadata": {**message.metadata, "gateway_response": result}
                }
            )
            logger.info(f"Message {message_id} sent successfully")
        else:
            # Check if should retry
            retry_manager = RetryManager()
            if retry_manager.should_retry(message_id):
                retry_manager.schedule_retry(
                    message_id,
                    "app.workers.message_worker.send_message",
                    message_id=message_id
                )
                message_crud.update_message(
                    db,
                    message_id,
                    {"status": MessageStatus.PENDING}
                )
            else:
                message_crud.update_message(
                    db,
                    message_id,
                    {
                        "status": MessageStatus.FAILED,
                        "metadata": {
                            **message.metadata,
                            "error": result.get("error"),
                            "max_retries_exceeded": True
                        }
                    }
                )
            logger.error(f"Message {message_id} failed: {result.get('error')}")
    
    except Exception as e:
        logger.error(f"Error sending message {message_id}: {e}")
    finally:
        db.close()


@celery_app.task(name="app.workers.message_worker.process_incoming_message")
def process_incoming_message(
    from_phone: str,
    message_text: str,
    external_id: str,
    metadata: dict = None
):
    """
    Process incoming WhatsApp message.
    
    Args:
        from_phone: Sender phone number
        message_text: Message text
        external_id: WhatsApp message ID
        metadata: Additional metadata
    """
    asyncio.run(_process_incoming_message_async(
        from_phone,
        message_text,
        external_id,
        metadata or {}
    ))


async def _process_incoming_message_async(
    from_phone: str,
    message_text: str,
    external_id: str,
    metadata: dict
):
    """Async incoming message processing."""
    db = next(get_db())
    
    try:
        from ..crud import contact as contact_crud
        
        # Find or create contact
        contact = contact_crud.get_contact_by_phone(db, from_phone)
        if not contact:
            contact = contact_crud.create_contact(
                db,
                {
                    "phone": from_phone,
                    "name": from_phone,
                    "metadata": {"auto_created": True}
                }
            )
        
        # Find related conversation
        conversation = conversation_crud.get_or_create_conversation(
            db,
            contact_id=contact.id
        )
        
        # Save incoming message
        message_crud.create_message(
            db,
            {
                "conversation_id": conversation.id,
                "contact_id": contact.id,
                "content": message_text,
                "direction": "inbound",
                "status": MessageStatus.DELIVERED,
                "external_id": external_id,
                "received_at": datetime.utcnow(),
                "metadata": metadata
            }
        )
        
        # Classify reply with AI
        if settings.AI_REPLY_CLASSIFICATION_ENABLED:
            classifier = ReplyClassifier()
            
            # Get conversation history
            history = message_crud.get_messages_by_conversation(db, conversation.id)
            history_texts = [msg.content for msg in history[-5:]]  # Last 5 messages
            
            # Get original message if this is a reply
            original_message = None
            if len(history) >= 2:
                original_message = history[-2].content
            
            # Classify
            classification = await classifier.classify_reply(
                message_text,
                original_message=original_message,
                conversation_history=history_texts
            )
            
            # Update conversation with classification
            conversation_crud.update_conversation(
                db,
                conversation.id,
                {
                    "last_reply_intent": classification.get("intent"),
                    "last_reply_sentiment": classification.get("sentiment"),
                    "metadata": {
                        **conversation.metadata,
                        "last_classification": classification,
                        "last_message_at": datetime.utcnow().isoformat()
                    }
                }
            )
            
            # Handle auto-response
            if classification.get("intent") == "unsubscribe":
                # Mark contact as unsubscribed
                contact_crud.update_contact(
                    db,
                    contact.id,
                    {"is_subscribed": False, "unsubscribed_at": datetime.utcnow()}
                )
                
                # Send confirmation
                gateway = WhatsAppGatewayConnector()
                await gateway.send_message(
                    to=from_phone,
                    message="You've been unsubscribed. You won't receive further messages from us."
                )
            
            # Check if auto-response needed
            auto_response_check = await classifier.should_auto_respond(classification)
            if auto_response_check.get("should_respond"):
                suggested_response = auto_response_check.get("suggested_response")
                if suggested_response:
                    gateway = WhatsAppGatewayConnector()
                    await gateway.send_message(
                        to=from_phone,
                        message=suggested_response
                    )
            
            logger.info(
                f"Processed incoming message from {from_phone}: "
                f"intent={classification.get('intent')}, "
                f"sentiment={classification.get('sentiment')}"
            )
    
    except Exception as e:
        logger.error(f"Error processing incoming message: {e}")
    finally:
        db.close()


@celery_app.task(name="app.workers.message_worker.cleanup_old_messages")
def cleanup_old_messages():
    """Clean up old messages from database."""
    db = next(get_db())
    
    try:
        # Delete messages older than 90 days
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        deleted_count = message_crud.delete_messages_before(db, cutoff_date)
        
        logger.info(f"Cleaned up {deleted_count} old messages")
    
    except Exception as e:
        logger.error(f"Error cleaning up old messages: {e}")
    finally:
        db.close()


@celery_app.task(name="app.workers.message_worker.update_message_status")
def update_message_status(message_id: int, status: str, metadata: dict = None):
    """
    Update message status (from webhook).
    
    Args:
        message_id: Message ID
        status: New status
        metadata: Additional metadata
    """
    db = next(get_db())
    
    try:
        update_data = {"status": status}
        
        if status == MessageStatus.DELIVERED:
            update_data["delivered_at"] = datetime.utcnow()
        elif status == MessageStatus.READ:
            update_data["read_at"] = datetime.utcnow()
        elif status == MessageStatus.FAILED:
            update_data["failed_at"] = datetime.utcnow()
        
        if metadata:
            message = message_crud.get_message(db, message_id)
            update_data["metadata"] = {**message.metadata, **metadata}
        
        message_crud.update_message(db, message_id, update_data)
        logger.info(f"Updated message {message_id} status to {status}")
    
    except Exception as e:
        logger.error(f"Error updating message status: {e}")
    finally:
        db.close()
