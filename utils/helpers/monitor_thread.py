
import threading
import time
import logging
import gc
import asyncio

logger = logging.getLogger("MONITOR_THREAD")
logger.setLevel(logging.INFO)

def start_tp_sl_monitor_thread():
    """Start the TP/SL monitor in a separate daemon thread"""
    logger.info("Starting TP/SL Monitor Thread...")
    
    # Create thread with unique name
    thread = threading.Thread(target=_monitor_loop, name="TPSL_Monitor", daemon=True)
    thread.start()
    return thread

def _monitor_loop():
    """Main monitoring loop"""
    logger.info("[OK] TP/SL Monitor Loop STARTED")
    
    orchestrator = None
    
    while True:
        try:
            # 1. Find Orchestrator Instance if not found
            if not orchestrator:
                # Look for CompleteUnifiedOrchestrator or ExecutionOrchestrator
                for obj in gc.get_objects():
                    if hasattr(obj, '__class__'):
                        name = obj.__class__.__name__
                        if name == 'CompleteUnifiedOrchestrator' or name == 'ExecutionOrchestrator':
                             # Check if it has monitor_positions method
                             if hasattr(obj, 'monitor_positions'):
                                 orchestrator = obj
                                 logger.info(f"[OK] FOUND ORCHESTRATOR: {name}")
                                 break
            
            # 2. Run Monitor Logic
            if orchestrator:
                # Need to handle async call if monitor_positions is async
                # Most orchestrators use async def monitor_positions.
                # We need a new event loop for this thread if strictly async, 
                # OR just call it if it's fire-and-forget.
                # BUT since we assume main loop is running, we can't easily jump into it.
                # SAFE BET: If the method is async, we use a new loop.
                
                if asyncio.iscoroutinefunction(orchestrator.monitor_positions):
                     # logger.info("Running async monitor...")
                     # Use new loop or run_until_complete
                     loop = asyncio.new_event_loop()
                     asyncio.set_event_loop(loop)
                     loop.run_until_complete(orchestrator.monitor_positions())
                     loop.close()
                else:
                     # Synchronous call
                     orchestrator.monitor_positions()
                
            else:
                logger.warning("⏳ Waiting for Orchestrator instance...")

        except Exception as e:
            logger.error(f" Monitor Loop Error: {e}")
        
        # Sleep 5s
        time.sleep(5)
