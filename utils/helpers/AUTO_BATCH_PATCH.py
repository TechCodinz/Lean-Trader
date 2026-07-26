
# AUTOMATIC BATCHING WRAPPER - Inserted by Phase 7.3/7.4 integration
import asyncio
from collections import defaultdict
import time

_signal_buffer = []
_last_flush = time.time()
_flush_task = None

async def _auto_flush_buffer():
    '''Auto-flush buffer every 500ms'''
    global _signal_buffer, _last_flush
    while True:
        await asyncio.sleep(0.5)
        if _signal_buffer and (time.time() - _last_flush) >= 0.5:
            await _execute_buffered_signals()
            _last_flush = time.time()

async def _execute_buffered_signals():
    '''Execute buffered signals with coalescence + parallel'''
    global _signal_buffer
    if not _signal_buffer:
        return
    
    signals = _signal_buffer[:]
    _signal_buffer.clear()
    
    # Use coalesced parallel execution
    if hasattr(self.execution_orchestrator, 'execute_coalesced_signals'):
        await self.execution_orchestrator.execute_coalesced_signals(signals)
    else:
        # Fallback
        for sig in signals:
            await self.execution_orchestrator.execute_signal(sig)

# Start auto-flush task
if not _flush_task:
    _flush_task = asyncio.create_task(_auto_flush_buffer())

