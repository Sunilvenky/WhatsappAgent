"""WhatsApp management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

from apps.api.app.connectors.whatsapp_gateway import get_whatsapp_connector
from apps.api.app.auth.dependencies import get_current_user
from apps.api.app.models.user import User

router = APIRouter()


class SendMessageRequest(BaseModel):
    """Request schema for sending a message."""
    to: str
    message: str
    options: Optional[dict] = None


class BulkMessageRequest(BaseModel):
    """Request schema for bulk messages."""
    messages: List[dict]


@router.get("/status")
async def get_whatsapp_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get WhatsApp connection status.
    Requires authentication.
    """
    try:
        connector = get_whatsapp_connector()
        status_info = await connector.get_connection_status()
        return {
            "success": True,
            "data": status_info
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"WhatsApp Gateway unavailable: {str(e)}"
        )


@router.get("/qr")
async def get_qr_code(
    current_user: User = Depends(get_current_user)
):
    """
    Get QR code for WhatsApp authentication.
    Only accessible by admin users.
    """
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can access QR codes"
        )
    
    try:
        connector = get_whatsapp_connector()
        qr_code = await connector.get_qr_code()
        
        if not qr_code:
            return {
                "success": True,
                "data": {
                    "qrCode": None,
                    "message": "Already authenticated"
                }
            }
        
        return {
            "success": True,
            "data": {
                "qrCode": qr_code,
                "message": "Scan this QR code with WhatsApp mobile app"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to get QR code: {str(e)}"
        )


@router.post("/logout")
async def logout_whatsapp(
    current_user: User = Depends(get_current_user)
):
    """
    Logout from WhatsApp.
    Only accessible by admin users.
    """
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can logout WhatsApp"
        )
    
    try:
        connector = get_whatsapp_connector()
        success = await connector.logout()
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to logout"
            )
        
        return {
            "success": True,
            "message": "Logged out successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to logout: {str(e)}"
        )


@router.post("/send")
async def send_message(
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Send a WhatsApp message directly.
    For testing and manual sending.
    """
    try:
        connector = get_whatsapp_connector()
        
        # Check if connected
        if not await connector.is_connected():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="WhatsApp not connected. Please scan QR code first."
            )
        
        # Send message
        result = await connector.send_message(
            to=request.to,
            message=request.message,
            options=request.options
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Message sent successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


@router.post("/send-bulk")
async def send_bulk_messages(
    request: BulkMessageRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Send multiple WhatsApp messages.
    For bulk operations.
    """
    if current_user.role.value not in ["admin", "marketer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and marketers can send bulk messages"
        )
    
    try:
        connector = get_whatsapp_connector()
        
        # Check if connected
        if not await connector.is_connected():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="WhatsApp not connected. Please scan QR code first."
            )
        
        # Send bulk messages
        results = await connector.send_bulk_messages(request.messages)
        
        return {
            "success": True,
            "data": results,
            "message": f"Sent {results.get('summary', {}).get('success', 0)} messages successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send bulk messages: {str(e)}"
        )


@router.get("/check-contact/{phone_number}")
async def check_contact(
    phone_number: str,
    current_user: User = Depends(get_current_user)
):
    """Check if a phone number exists on WhatsApp."""
    try:
        connector = get_whatsapp_connector()
        
        # Check if connected
        if not await connector.is_connected():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="WhatsApp not connected"
            )
        
        # Check contact
        contact_info = await connector.check_contact_exists(phone_number)
        
        return {
            "success": True,
            "data": contact_info
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check contact: {str(e)}"
        )


@router.get("/health")
async def whatsapp_health():
    """Check WhatsApp Gateway health (no authentication required)."""
    try:
        connector = get_whatsapp_connector()
        health = await connector.health_check()
        
        return {
            "success": True,
            "data": health
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "WhatsApp Gateway is unavailable"
        }
