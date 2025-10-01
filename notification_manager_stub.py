"""Stub implementation for NotificationManager"""
import asyncio
import logging

logger = logging.getLogger(__name__)

class NotificationManager:
    """Stub Notification Manager implementation"""
    
    def __init__(self):
        self.channels = []
        logger.warning("Using stub NotificationManager implementation")
    
    async def initialize(self):
        """Initialize the notification manager"""
        logger.info("Initializing stub NotificationManager")
        return True
    
    async def send_notification(self, title, message, channel=None):
        """Send a notification"""
        logger.info(f"Notification: {title} - {message}")
        return True
    
    async def is_healthy(self):
        """Check if notification manager is healthy"""
        return True