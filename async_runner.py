#!/usr/bin/env python3
"""
LeanTrader Async Runner - hosts async systems concurrently.

Architecture:
- Each async system runs as an asyncio Task
- Systems communicate via signal_bus
- Sync trader (zoo_paper_trader) runs separately, reads from bus
"""
import asyncio
import logging
import sys
sys.path.insert(0, '/app')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ASYNC_RUNNER')

class AsyncRunner:
    def __init__(self):
        self.tasks = []
        self.systems = {}
    
    def register(self, name, coro_func, *args, **kwargs):
        """Register an async system to run."""
        self.systems[name] = (coro_func, args, kwargs)
        logger.info(f"Registered async system: {name}")
    
    async def run_all(self):
        """Run all registered systems concurrently."""
        tasks = []
        for name, (func, args, kwargs) in self.systems.items():
            task = asyncio.create_task(func(*args, **kwargs), name=name)
            tasks.append(task)
            logger.info(f"Started: {name}")
        await asyncio.gather(*tasks, return_exceptions=True)

async def main():
    runner = AsyncRunner()
    # Systems will be registered here
    logger.info("Async Runner ready - awaiting system registration")
    await runner.run_all()

if __name__ == '__main__':
    asyncio.run(main())
