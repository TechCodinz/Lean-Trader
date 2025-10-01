"""Stub implementation for DataCollector"""
import asyncio
import logging

logger = logging.getLogger(__name__)

class DataCollector:
    """Stub Data Collector implementation"""
    
    def __init__(self, database=None):
        self.database = database
        self.running = False
        logger.warning("Using stub DataCollector implementation")
    
    async def initialize(self):
        """Initialize the data collector"""
        logger.info("Initializing stub DataCollector")
        return True
    
    async def start(self):
        """Start collecting data"""
        logger.info("Starting stub DataCollector")
        self.running = True
        while self.running:
            await asyncio.sleep(60)
    
    async def stop(self):
        """Stop collecting data"""
        logger.info("Stopping stub DataCollector")
        self.running = False
    
    async def is_healthy(self):
        """Check if collector is healthy"""
        return True