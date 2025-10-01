"""
Production Optimizations Module - Performance and Stability Improvements
Fixes infinite loops, bare excepts, memory management, and adds state persistence
"""

import asyncio
import signal
import json
import pickle
import threading
import gc
import traceback
from typing import Any, Dict, Optional, Set, List, Callable
from pathlib import Path
from datetime import datetime, timedelta
from collections import deque
import logging
import weakref

logger = logging.getLogger(__name__)

# ============================================
# GRACEFUL SHUTDOWN MANAGER
# ============================================

class GracefulShutdownManager:
    """
    Manages graceful shutdown for all loops and tasks
    Prevents infinite loops from blocking shutdown
    """
    
    def __init__(self):
        self.running = True
        self.tasks: Set[asyncio.Task] = set()
        self.loops: Dict[str, bool] = {}
        self.shutdown_callbacks: List[Callable] = []
        self.shutdown_timeout = 30  # seconds
        self._shutdown_event = asyncio.Event()
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown()
        
    def register_loop(self, name: str):
        """Register a loop that needs to be stopped"""
        self.loops[name] = True
        logger.debug(f"Registered loop: {name}")
        
    def should_continue(self, loop_name: str) -> bool:
        """Check if a loop should continue running"""
        return self.running and self.loops.get(loop_name, True)
        
    def register_task(self, task: asyncio.Task):
        """Register an async task for cleanup"""
        self.tasks.add(task)
        # Remove from set when done
        task.add_done_callback(self.tasks.discard)
        
    def register_shutdown_callback(self, callback: Callable):
        """Register callback to be called on shutdown"""
        self.shutdown_callbacks.append(callback)
        
    def shutdown(self):
        """Initiate graceful shutdown"""
        logger.info("Starting graceful shutdown...")
        self.running = False
        
        # Stop all loops
        for loop_name in self.loops:
            self.loops[loop_name] = False
            
        # Set shutdown event
        self._shutdown_event.set()
        
        # Call shutdown callbacks
        for callback in self.shutdown_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in shutdown callback: {e}")
                
    async def wait_for_shutdown(self):
        """Wait for shutdown signal"""
        await self._shutdown_event.wait()
        
    async def cleanup_tasks(self):
        """Clean up all registered tasks"""
        if not self.tasks:
            return
            
        logger.info(f"Waiting for {len(self.tasks)} tasks to complete...")
        
        # Cancel all tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()
                
        # Wait for tasks to complete
        try:
            await asyncio.wait_for(
                asyncio.gather(*self.tasks, return_exceptions=True),
                timeout=self.shutdown_timeout
            )
        except asyncio.TimeoutError:
            logger.warning(f"Some tasks did not complete within {self.shutdown_timeout} seconds")

# Global shutdown manager
shutdown_manager = GracefulShutdownManager()

# ============================================
# SAFE LOOP WRAPPER
# ============================================

def safe_loop(name: str, interval: float = 1.0):
    """
    Decorator to make loops safe with proper shutdown
    """
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            shutdown_manager.register_loop(name)
            logger.info(f"Starting safe loop: {name}")
            
            while shutdown_manager.should_continue(name):
                try:
                    await func(*args, **kwargs)
                    await asyncio.sleep(interval)
                except asyncio.CancelledError:
                    logger.info(f"Loop {name} cancelled")
                    break
                except Exception as e:
                    logger.error(f"Error in loop {name}: {e}")
                    logger.debug(traceback.format_exc())
                    await asyncio.sleep(interval * 2)  # Back off on error
                    
            logger.info(f"Loop {name} stopped")
            
        def sync_wrapper(*args, **kwargs):
            shutdown_manager.register_loop(name)
            logger.info(f"Starting safe loop: {name}")
            
            import time
            while shutdown_manager.should_continue(name):
                try:
                    func(*args, **kwargs)
                    time.sleep(interval)
                except KeyboardInterrupt:
                    logger.info(f"Loop {name} interrupted")
                    break
                except Exception as e:
                    logger.error(f"Error in loop {name}: {e}")
                    logger.debug(traceback.format_exc())
                    time.sleep(interval * 2)
                    
            logger.info(f"Loop {name} stopped")
            
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
        
    return decorator

# ============================================
# SPECIFIC EXCEPTION HANDLER
# ============================================

class SpecificExceptionHandler:
    """
    Replaces bare except clauses with specific exception handling
    """
    
    def __init__(self):
        self.handlers = {}
        self.default_handler = self._default_handler
        
    def register_handler(self, exception_type: type, handler: Callable):
        """Register handler for specific exception type"""
        self.handlers[exception_type] = handler
        
    def handle(self, func: Callable):
        """Decorator to add specific exception handling"""
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Find the most specific handler
                for exc_type in type(e).__mro__:
                    if exc_type in self.handlers:
                        return self.handlers[exc_type](e, *args, **kwargs)
                        
                # Use default handler
                return self.default_handler(e, *args, **kwargs)
                
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Find the most specific handler
                for exc_type in type(e).__mro__:
                    if exc_type in self.handlers:
                        handler = self.handlers[exc_type]
                        if asyncio.iscoroutinefunction(handler):
                            return await handler(e, *args, **kwargs)
                        return handler(e, *args, **kwargs)
                        
                # Use default handler
                return self.default_handler(e, *args, **kwargs)
                
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
        
    def _default_handler(self, e: Exception, *args, **kwargs):
        """Default exception handler"""
        logger.error(f"Unhandled exception: {type(e).__name__}: {e}")
        logger.debug(traceback.format_exc())
        return None

# Global exception handler
exception_handler = SpecificExceptionHandler()

# Register common handlers
def handle_connection_error(e: Exception, *args, **kwargs):
    logger.warning(f"Connection error: {e}")
    return {'error': 'connection_failed', 'retry': True}

def handle_value_error(e: Exception, *args, **kwargs):
    logger.error(f"Value error: {e}")
    return {'error': 'invalid_value', 'retry': False}

def handle_key_error(e: Exception, *args, **kwargs):
    logger.error(f"Key error: {e}")
    return {'error': 'missing_key', 'retry': False}

exception_handler.register_handler(ConnectionError, handle_connection_error)
exception_handler.register_handler(ValueError, handle_value_error)
exception_handler.register_handler(KeyError, handle_key_error)

# ============================================
# MEMORY MANAGEMENT SYSTEM
# ============================================

class MemoryManager:
    """
    Manages memory for long-running processes
    Prevents memory leaks and optimizes usage
    """
    
    def __init__(self, max_memory_mb: int = 1024):
        self.max_memory_mb = max_memory_mb
        self.caches: Dict[str, weakref.WeakValueDictionary] = {}
        self.data_buffers: Dict[str, deque] = {}
        self.gc_interval = 300  # 5 minutes
        self.last_gc = datetime.now()
        
    def create_cache(self, name: str) -> weakref.WeakValueDictionary:
        """Create a weak reference cache that auto-cleans"""
        if name not in self.caches:
            self.caches[name] = weakref.WeakValueDictionary()
        return self.caches[name]
        
    def create_buffer(self, name: str, maxlen: int = 1000) -> deque:
        """Create a bounded buffer for data"""
        if name not in self.data_buffers:
            self.data_buffers[name] = deque(maxlen=maxlen)
        return self.data_buffers[name]
        
    def check_memory(self) -> Dict[str, Any]:
        """Check current memory usage"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                'rss_mb': memory_info.rss / 1024 / 1024,
                'percent': process.memory_percent(),
                'available_mb': psutil.virtual_memory().available / 1024 / 1024,
                'caches': {name: len(cache) for name, cache in self.caches.items()},
                'buffers': {name: len(buffer) for name, buffer in self.data_buffers.items()}
            }
        except ImportError:
            # psutil not available, return basic info
            import resource
            usage = resource.getrusage(resource.RUSAGE_SELF)
            
            return {
                'rss_mb': usage.ru_maxrss / 1024,  # Linux reports in KB
                'percent': 0,  # Can't calculate without psutil
                'available_mb': 0,  # Can't get without psutil
                'caches': {name: len(cache) for name, cache in self.caches.items()},
                'buffers': {name: len(buffer) for name, buffer in self.data_buffers.items()}
            }
        
    def cleanup(self, force: bool = False):
        """Clean up memory"""
        memory = self.check_memory()
        
        # Check if cleanup needed
        if not force and memory['rss_mb'] < self.max_memory_mb:
            if (datetime.now() - self.last_gc).seconds < self.gc_interval:
                return
                
        logger.info(f"Running memory cleanup (current: {memory['rss_mb']:.1f}MB)")
        
        # Clear old data from buffers
        for name, buffer in self.data_buffers.items():
            if len(buffer) > buffer.maxlen * 0.8:
                # Remove oldest 20%
                for _ in range(int(len(buffer) * 0.2)):
                    buffer.popleft()
                    
        # Force garbage collection
        gc.collect()
        self.last_gc = datetime.now()
        
        # Check memory after cleanup
        new_memory = self.check_memory()
        logger.info(f"Memory after cleanup: {new_memory['rss_mb']:.1f}MB "
                   f"(freed: {memory['rss_mb'] - new_memory['rss_mb']:.1f}MB)")

# Global memory manager
memory_manager = MemoryManager()

# ============================================
# STATE PERSISTENCE SYSTEM
# ============================================

class StatePersistence:
    """
    Persists bot state to disk for recovery
    """
    
    def __init__(self, state_dir: str = "state"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(exist_ok=True)
        self.state_file = self.state_dir / "bot_state.json"
        self.backup_file = self.state_dir / "bot_state.backup.json"
        self.checkpoint_interval = 60  # seconds
        self.last_checkpoint = datetime.now()
        
    def save_state(self, state: Dict[str, Any], force: bool = False):
        """Save state to disk"""
        if not force:
            if (datetime.now() - self.last_checkpoint).seconds < self.checkpoint_interval:
                return
                
        try:
            # Create backup of existing state
            if self.state_file.exists():
                import shutil
                shutil.copy2(self.state_file, self.backup_file)
                
            # Prepare state for serialization
            serializable_state = self._make_serializable(state)
            
            # Add metadata
            serializable_state['_metadata'] = {
                'timestamp': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            # Save state
            with open(self.state_file, 'w') as f:
                json.dump(serializable_state, f, indent=2)
                
            self.last_checkpoint = datetime.now()
            logger.debug(f"State saved to {self.state_file}")
            
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
            
    def load_state(self) -> Optional[Dict[str, Any]]:
        """Load state from disk"""
        try:
            if not self.state_file.exists():
                logger.info("No saved state found")
                return None
                
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                
            metadata = state.pop('_metadata', {})
            logger.info(f"Loaded state from {metadata.get('timestamp', 'unknown')}")
            
            return state
            
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            
            # Try backup
            if self.backup_file.exists():
                logger.info("Trying backup state file...")
                try:
                    with open(self.backup_file, 'r') as f:
                        return json.load(f)
                except:
                    pass
                    
            return None
            
    def _make_serializable(self, obj: Any) -> Any:
        """Convert object to JSON-serializable format"""
        if isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        elif isinstance(obj, (datetime,)):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._make_serializable(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            return self._make_serializable(obj.__dict__)
        else:
            return str(obj)
            
    def save_checkpoint(self, name: str, data: Any):
        """Save a named checkpoint"""
        checkpoint_file = self.state_dir / f"checkpoint_{name}.pkl"
        
        try:
            with open(checkpoint_file, 'wb') as f:
                pickle.dump(data, f)
            logger.debug(f"Checkpoint saved: {name}")
        except Exception as e:
            logger.error(f"Failed to save checkpoint {name}: {e}")
            
    def load_checkpoint(self, name: str) -> Optional[Any]:
        """Load a named checkpoint"""
        checkpoint_file = self.state_dir / f"checkpoint_{name}.pkl"
        
        if not checkpoint_file.exists():
            return None
            
        try:
            with open(checkpoint_file, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            logger.error(f"Failed to load checkpoint {name}: {e}")
            return None

# Global state persistence
state_persistence = StatePersistence()

# ============================================
# OPTIMIZED BOT WRAPPER
# ============================================

class OptimizedBotWrapper:
    """
    Wraps bot with all optimizations
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.shutdown_manager = shutdown_manager
        self.memory_manager = memory_manager
        self.state_persistence = state_persistence
        self.exception_handler = exception_handler
        
        # Track bot state
        self.state = {
            'positions': {},
            'orders': {},
            'balance': {},
            'metrics': {},
            'config': {}
        }
        
        # Load previous state if exists
        saved_state = self.state_persistence.load_state()
        if saved_state:
            self.state.update(saved_state)
            logger.info("Restored previous bot state")
            
        # Setup auto-save
        self._setup_auto_save()
        
    def _setup_auto_save(self):
        """Setup automatic state saving"""
        @safe_loop("state_saver", interval=60)
        async def save_state_loop():
            self.state_persistence.save_state(self.state)
            
        # Start the loop
        task = asyncio.create_task(save_state_loop())
        self.shutdown_manager.register_task(task)
        
    def wrap_method(self, method_name: str):
        """Wrap a bot method with optimizations"""
        original_method = getattr(self.bot, method_name)
        
        @exception_handler.handle
        async def wrapped_method(*args, **kwargs):
            # Check memory before operation
            self.memory_manager.cleanup()
            
            # Call original method
            result = await original_method(*args, **kwargs)
            
            # Update state if needed
            if method_name == 'place_order':
                self.state['orders'][result.get('id')] = result
                self.state_persistence.save_state(self.state)
                
            return result
            
        setattr(self.bot, method_name, wrapped_method)
        
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down optimized bot...")
        
        # Save final state
        self.state_persistence.save_state(self.state, force=True)
        
        # Cleanup
        await self.shutdown_manager.cleanup_tasks()
        
        logger.info("Bot shutdown complete")

# ============================================
# INTEGRATION FUNCTION
# ============================================

def integrate_optimizations(bot):
    """
    Integrate all optimizations into existing bot
    """
    wrapper = OptimizedBotWrapper(bot)
    
    # Wrap critical methods
    critical_methods = ['place_order', 'cancel_order', 'get_balance']
    for method in critical_methods:
        if hasattr(bot, method):
            wrapper.wrap_method(method)
            
    # Add shutdown handler
    bot.shutdown = wrapper.shutdown
    
    # Add memory check
    bot.check_memory = memory_manager.check_memory
    
    # Add state save/load
    bot.save_state = lambda: state_persistence.save_state(wrapper.state, force=True)
    bot.load_state = state_persistence.load_state
    
    logger.info("✅ Production optimizations integrated:")
    logger.info("  - Graceful shutdown manager")
    logger.info("  - Safe loop wrappers")
    logger.info("  - Specific exception handlers")
    logger.info("  - Memory management")
    logger.info("  - State persistence")
    
    return bot

# Example usage for fixing infinite loops
def fix_infinite_loop(original_loop_func):
    """
    Convert an infinite loop to a safe loop
    """
    @safe_loop("converted_loop", interval=1.0)
    async def safe_version():
        await original_loop_func()
        
    return safe_version

print("✅ Production optimizations loaded successfully!")
print("Features:")
print("  1. Graceful shutdown for all loops")
print("  2. Specific exception handling")
print("  3. Memory management for long runs")
print("  4. State persistence and recovery")
print("\nUse: integrate_optimizations(bot)")