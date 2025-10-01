"""Stub implementation for Dashboard"""
import asyncio
import logging

logger = logging.getLogger(__name__)

class Dashboard:
    """Stub Dashboard implementation"""
    
    def __init__(self, bot=None, database=None):
        self.bot = bot
        self.database = database
        self.running = False
        logger.warning("Using stub Dashboard implementation")
    
    async def initialize(self):
        """Initialize the dashboard"""
        logger.info("Initializing stub Dashboard")
        return True
    
    async def start(self):
        """Start the dashboard"""
        logger.info("Starting stub Dashboard")
        self.running = True
        while self.running:
            await asyncio.sleep(60)
    
    async def stop(self):
        """Stop the dashboard"""
        logger.info("Stopping stub Dashboard")
        self.running = False
    
    async def is_healthy(self):
        """Check if dashboard is healthy"""
        return True