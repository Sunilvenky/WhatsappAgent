"""Conversation and message management API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from apps.api.app.core.database import get_db
from apps.api.app.crud import (
    conversation as conversation_crud,
    message as message_crud,
    reply as reply_crud
)
from apps.api.app.schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse
)
from apps.api.app.schemas.message import (
    MessageCreate,
    MessageResponse,
    ReplyCreate,
    ReplyResponse
)
from apps.api.app.models.conversation import ConversationStatus
from apps.api.app.models.message import MessageDirection, MessageStatus
from apps.api.app.auth.dependencies import get_current_user
from apps.api.app.models.user import User

router = APIRouter()


# Conversation endpoints
@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(
    conversation: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new conversation."""
    try:
        db_conversation = conversation_crud.create(
            db, 
            **conversation.model_dump()
        )
        return db_conversation
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create conversation: {str(e)}"
        )


@router.get("/", response_model=List[ConversationResponse])
def list_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    contact_id: Optional[int] = Query(None),
    assigned_to: Optional[int] = Query(None),
    status: Optional[ConversationStatus] = Query(None),
    priority: Optional[str] = Query(None),
    has_unread: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List conversations with optional filtering."""
    # If not admin and no assigned_to specified, show user's assigned conversations
    if current_user.role.value != "admin" and assigned_to is None:
        assigned_to = current_user.id
    
    conversations = conversation_crud.get_multi(
        db,
        skip=skip,
        limit=limit,
        contact_id=contact_id,
        assigned_to=assigned_to,
        status=status,
        priority=priority
    )
    
    # Filter by unread messages if requested
    if has_unread is True:
        conversations = [c for c in conversations if c.has_unread_messages]
    elif has_unread is False:
        conversations = [c for c in conversations if not c.has_unread_messages]
    
    return conversations


@router.get("/assigned", response_model=List[ConversationResponse])
def get_assigned_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get conversations assigned to the current user."""
    conversations = conversation_crud.get_assigned_conversations(
        db, 
        current_user.id,
        skip=skip,
        limit=limit
    )
    return conversations


@router.get("/urgent", response_model=List[ConversationResponse])
def get_urgent_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get urgent conversations for the current user."""
    conversations = conversation_crud.get_urgent_conversations(
        db, 
        current_user.id,
        skip=skip,
        limit=limit
    )
    return conversations


@router.get("/unread", response_model=List[ConversationResponse])
def get_unread_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get conversations with unread messages for the current user."""
    conversations = conversation_crud.get_conversations_with_unread(
        db, 
        current_user.id,
        skip=skip,
        limit=limit
    )
    return conversations


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific conversation by ID."""
    conversation = conversation_crud.get(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Check access permissions
    if (conversation.assigned_to != current_user.id and 
        current_user.role.value not in ["admin", "marketer"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation"
        )
    
    return conversation


@router.put("/{conversation_id}", response_model=ConversationResponse)
def update_conversation(
    conversation_id: int,
    conversation_update: ConversationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a conversation."""
    conversation = conversation_crud.get(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Check update permissions
    if (conversation.assigned_to != current_user.id and 
        current_user.role.value not in ["admin", "marketer"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this conversation"
        )
    
    updated_conversation = conversation_crud.update(
        db, 
        conversation, 
        **conversation_update.model_dump(exclude_unset=True)
    )
    return updated_conversation


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a conversation."""
    conversation = conversation_crud.get(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Check delete permissions (admin only)
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete conversations"
        )
    
    conversation_crud.delete(db, conversation_id)


@router.post("/{conversation_id}/assign", response_model=ConversationResponse)
def assign_conversation(
    conversation_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign a conversation to a user."""
    conversation = conversation_crud.get(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Check assignment permissions
    if current_user.role.value not in ["admin", "marketer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to assign conversations"
        )
    
    success = conversation_crud.assign_conversation(db, conversation_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to assign conversation"
        )
    
    db.refresh(conversation)
    return conversation


@router.post("/{conversation_id}/close", response_model=ConversationResponse)
def close_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Close a conversation."""
    conversation = conversation_crud.get(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Check close permissions
    if (conversation.assigned_to != current_user.id and 
        current_user.role.value not in ["admin", "marketer"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to close this conversation"
        )
    
    success = conversation_crud.close_conversation(db, conversation_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to close conversation"
        )
    
    db.refresh(conversation)
    return conversation


@router.post("/{conversation_id}/reopen", response_model=ConversationResponse)
def reopen_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reopen a closed conversation."""
    conversation = conversation_crud.get(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Check reopen permissions
    if current_user.role.value not in ["admin", "marketer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to reopen conversations"
        )
    
    if conversation.status != ConversationStatus.CLOSED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only closed conversations can be reopened"
        )
    
    updated_conversation = conversation_crud.update(
        db, 
        conversation, 
        status=ConversationStatus.ACTIVE
    )
    return updated_conversation


# Message endpoints
@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
def get_conversation_messages(
    conversation_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get messages for a conversation."""
    conversation = conversation_crud.get(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Check access permissions
    if (conversation.assigned_to != current_user.id and 
        current_user.role.value not in ["admin", "marketer"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this conversation"
        )
    
    messages = message_crud.get_conversation_messages(
        db, 
        conversation_id,
        skip=skip,
        limit=limit
    )
    return messages


@router.post("/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def send_message(
    conversation_id: int,
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a message in a conversation."""
    conversation = conversation_crud.get(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Check send permissions
    if (conversation.assigned_to != current_user.id and 
        current_user.role.value not in ["admin", "marketer"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to send messages in this conversation"
        )
    
    try:
        message_data = message.model_dump()
        message_data["conversation_id"] = conversation_id
        message_data["direction"] = MessageDirection.OUTBOUND
        
        db_message = message_crud.create(db, **message_data)
        
        # Update conversation last message
        conversation_crud.update_last_message(db, conversation_id, from_contact=False)
        
        return db_message
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to send message: {str(e)}"
        )


@router.put("/messages/{message_id}/status", response_model=MessageResponse)
def update_message_status(
    message_id: int,
    status: MessageStatus,
    whatsapp_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update message status (sent, delivered, read, failed)."""
    message = message_crud.get(db, message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    try:
        if status == MessageStatus.SENT:
            updated_message = message_crud.mark_sent(db, message_id, whatsapp_id)
        elif status == MessageStatus.DELIVERED:
            updated_message = message_crud.mark_delivered(db, message_id)
        elif status == MessageStatus.READ:
            updated_message = message_crud.mark_read(db, message_id)
        elif status == MessageStatus.FAILED:
            updated_message = message_crud.mark_failed(db, message_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}"
            )
        
        return updated_message
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update message status: {str(e)}"
        )


@router.get("/messages/{message_id}", response_model=MessageResponse)
def get_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific message by ID."""
    message = message_crud.get(db, message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Check access permissions through conversation
    conversation = conversation_crud.get(db, message.conversation_id)
    if (conversation.assigned_to != current_user.id and 
        current_user.role.value not in ["admin", "marketer"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this message"
        )
    
    return message


# Reply endpoints
@router.post("/{conversation_id}/replies", response_model=ReplyResponse, status_code=status.HTTP_201_CREATED)
def create_reply(
    conversation_id: int,
    reply: ReplyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a reply to a message."""
    conversation = conversation_crud.get(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    try:
        reply_data = reply.model_dump()
        reply_data["conversation_id"] = conversation_id
        
        db_reply = reply_crud.create(db, **reply_data)
        
        # Update conversation last message
        conversation_crud.update_last_message(db, conversation_id, from_contact=True)
        
        return db_reply
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create reply: {str(e)}"
        )


@router.get("/{conversation_id}/replies", response_model=List[ReplyResponse])
def get_conversation_replies(
    conversation_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get replies for a conversation."""
    conversation = conversation_crud.get(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    replies = reply_crud.get_conversation_replies(
        db, 
        conversation_id,
        skip=skip,
        limit=limit
    )
    return replies


@router.get("/stats/overview")
def get_conversation_stats(
    assigned_to: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get conversation statistics overview."""
    # If not admin and no assigned_to specified, show user's stats
    if current_user.role.value != "admin" and assigned_to is None:
        assigned_to = current_user.id
    
    # Get conversations
    all_conversations = conversation_crud.get_multi(
        db, 
        assigned_to=assigned_to,
        limit=1000
    )
    
    # Calculate statistics
    total_conversations = len(all_conversations)
    active_conversations = len([c for c in all_conversations if c.status == ConversationStatus.ACTIVE])
    closed_conversations = len([c for c in all_conversations if c.status == ConversationStatus.CLOSED])
    unread_conversations = len([c for c in all_conversations if c.has_unread_messages])
    
    return {
        "total_conversations": total_conversations,
        "active_conversations": active_conversations,
        "closed_conversations": closed_conversations,
        "unread_conversations": unread_conversations,
        "response_rate": round((closed_conversations / total_conversations * 100) if total_conversations > 0 else 0, 2)
    }