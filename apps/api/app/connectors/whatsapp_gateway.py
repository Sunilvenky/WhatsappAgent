"""WhatsApp Gateway Connector for Python API."""

import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from apps.api.app.core.config import settings

logger = logging.getLogger(__name__)


class WhatsAppGatewayConnector:
    """
    Connector for WhatsApp Gateway service.
    Provides async methods to interact with the Baileys-based WhatsApp Gateway.
    """
    
    def __init__(
        self,
        base_url: str = None,
        api_key: str = None,
        timeout: int = 30
    ):
        self.base_url = base_url or getattr(settings, 'WHATSAPP_GATEWAY_URL', 'http://localhost:3001')
        self.api_key = api_key or getattr(settings, 'WHATSAPP_GATEWAY_API_KEY', None)
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            headers = {}
            if self.api_key:
                headers['X-API-Key'] = self.api_key
            headers['Content-Type'] = 'application/json'
            
            self._session = aiohttp.ClientSession(
                headers=headers,
                timeout=self.timeout
            )
        return self._session
    
    async def close(self):
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to gateway."""
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with session.request(
                method,
                url,
                json=data,
                params=params
            ) as response:
                result = await response.json()
                
                if response.status >= 400:
                    error_msg = result.get('error', {})
                    if isinstance(error_msg, dict):
                        error_msg = error_msg.get('message', 'Unknown error')
                    raise Exception(f"Gateway error ({response.status}): {error_msg}")
                
                return result
                
        except aiohttp.ClientError as e:
            logger.error(f"Gateway request failed: {e}")
            raise Exception(f"Failed to connect to WhatsApp Gateway: {str(e)}")
    
    # Authentication Methods
    
    async def get_qr_code(self) -> Optional[str]:
        """
        Get QR code for WhatsApp authentication.
        Returns base64 encoded QR code image or None if already authenticated.
        """
        try:
            result = await self._request('GET', '/auth/qr')
            qr_code = result.get('data', {}).get('qrCode')
            return qr_code
        except Exception as e:
            logger.error(f"Failed to get QR code: {e}")
            raise
    
    async def get_connection_status(self) -> Dict[str, Any]:
        """
        Get WhatsApp connection status.
        Returns connection info including status, message count, etc.
        """
        try:
            result = await self._request('GET', '/auth/status')
            return result.get('data', {})
        except Exception as e:
            logger.error(f"Failed to get connection status: {e}")
            raise
    
    async def is_connected(self) -> bool:
        """Check if WhatsApp is connected."""
        try:
            status = await self.get_connection_status()
            return status.get('isConnected', False)
        except:
            return False
    
    async def logout(self) -> bool:
        """Logout from WhatsApp."""
        try:
            await self._request('POST', '/auth/logout')
            return True
        except Exception as e:
            logger.error(f"Failed to logout: {e}")
            return False
    
    # Messaging Methods
    
    async def send_message(
        self,
        to: str,
        message: str,
        options: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Send a single WhatsApp message.
        
        Args:
            to: Phone number with country code (e.g., +919900990099)
            message: Message text to send
            options: Optional message options
        
        Returns:
            Dict with messageId and timestamp
        """
        try:
            data = {
                'to': to,
                'message': message,
            }
            if options:
                data['options'] = options
            
            result = await self._request('POST', '/messages/send', data=data)
            return result.get('data', {})
        except Exception as e:
            logger.error(f"Failed to send message to {to}: {e}")
            raise
    
    async def send_bulk_messages(
        self,
        messages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Send multiple messages.
        
        Args:
            messages: List of message dicts with 'to' and 'message' keys
        
        Returns:
            Dict with results and summary
        """
        try:
            data = {'messages': messages}
            result = await self._request('POST', '/messages/bulk', data=data)
            return result.get('data', {})
        except Exception as e:
            logger.error(f"Failed to send bulk messages: {e}")
            raise
    
    # Contact Methods
    
    async def check_contact_exists(self, phone_number: str) -> Dict[str, Any]:
        """
        Check if a phone number exists on WhatsApp.
        
        Args:
            phone_number: Phone number to check
        
        Returns:
            Dict with exists, jid, and number fields
        """
        try:
            result = await self._request(
                'GET',
                f'/contacts/check/{phone_number}'
            )
            return result.get('data', {})
        except Exception as e:
            logger.error(f"Failed to check contact {phone_number}: {e}")
            raise
    
    # Health Check
    
    async def health_check(self) -> Dict[str, Any]:
        """Get gateway health status."""
        try:
            result = await self._request('GET', '/health')
            return result.get('data', {})
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise


# Global connector instance
_connector: Optional[WhatsAppGatewayConnector] = None


def get_whatsapp_connector() -> WhatsAppGatewayConnector:
    """Get or create global WhatsApp connector instance."""
    global _connector
    if _connector is None:
        _connector = WhatsAppGatewayConnector()
    return _connector


async def close_whatsapp_connector():
    """Close global WhatsApp connector."""
    global _connector
    if _connector:
        await _connector.close()
        _connector = None
