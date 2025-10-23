"""
Models package for the WhatsApp Agent API.
"""

from .user import User, UserRole
from .contact import Contact
from .phone_number import PhoneNumber
from .campaign import Campaign, CampaignStatus, CampaignType
from .message import Message, MessageStatus, MessageType, MessageDirection
from .conversation import Conversation, ConversationStatus
from .reply import Reply, ReplyStatus, ReplyType
from .unsubscriber import Unsubscriber, UnsubscribeReason, UnsubscribeMethod
from .lead import Lead, LeadStatus, LeadSource, LeadPriority

__all__ = [
    # User models
    "User",
    "UserRole",
    
    # Contact models
    "Contact",
    "PhoneNumber",
    
    # Campaign models
    "Campaign",
    "CampaignStatus",
    "CampaignType",
    
    # Message models
    "Message",
    "MessageStatus",
    "MessageType",
    "MessageDirection",
    
    # Conversation models
    "Conversation",
    "ConversationStatus",
    
    # Reply models
    "Reply",
    "ReplyStatus",
    "ReplyType",
    
    # Unsubscriber models
    "Unsubscriber",
    "UnsubscribeReason",
    "UnsubscribeMethod",
    
    # Lead models
    "Lead",
    "LeadStatus",
    "LeadSource",
    "LeadPriority",
]