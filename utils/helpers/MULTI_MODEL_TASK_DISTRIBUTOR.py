#!/usr/bin/env python3
"""
>> MULTI-MODEL TASK DISTRIBUTOR
Spawns multiple models to handle different tasks simultaneously
Distributes load intelligently across workers
"""

import logging
import asyncio
from typing import Dict, List, Any, Callable, Optional
from datetime import datetime
from collections import deque
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import psutil

logger = logging.getLogger(__name__)


class TaskWorker:
    """Individual task worker"""
    
    def __init__(self, worker_id: int, specialty: str):
        self.worker_id = worker_id
        self.specialty = specialty  # 'analysis', 'execution', 'monitoring', 'learning'
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.is_busy = False
        self.current_task = None
        self.performance_score = 1.0
        
        logger.debug(f"👷 Worker {worker_id} ({specialty}) initialized")
    
    async def execute_task(self, task: Dict) -> Dict:
        """Execute a task"""
        self.is_busy = True
        self.current_task = task
        start_time = datetime.now()
        
        try:
            # Execute task function
            func = task['function']
            args = task.get('args', [])
            kwargs = task.get('kwargs', {})
            
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Success
            self.tasks_completed += 1
            duration = (datetime.now() - start_time).total_seconds()
            
            # Update performance score (faster = better)
            self.performance_score = 0.9 * self.performance_score + 0.1 * (1.0 / max(duration, 0.1))
            
            return {
                'status': 'success',
                'result': result,
                'worker_id': self.worker_id,
                'duration': duration
            }
            
        except Exception as e:
            self.tasks_failed += 1
            logger.error(f"[X] Worker {self.worker_id} failed task: {e}")
            
            return {
                'status': 'failed',
                'error': str(e),
                'worker_id': self.worker_id
            }
            
        finally:
            self.is_busy = False
            self.current_task = None


class MultiModelTaskDistributor:
    """
    >> INTELLIGENT TASK DISTRIBUTION SYSTEM
    
    Features:
    - Spawns multiple worker models
    - Distributes tasks by specialty
    - Load balancing
    - Auto-scaling based on CPU/memory
    - Task prioritization
    - Failure recovery
    """
    
    def __init__(self, max_workers: Optional[int] = None):
        # Auto-detect optimal worker count
        if max_workers is None:
            cpu_count = psutil.cpu_count()
            max_workers = max(2, cpu_count - 1)  # Leave 1 core free
        
        self.max_workers = max_workers
        self.workers: Dict[str, List[TaskWorker]] = {
            'analysis': [],
            'execution': [],
            'monitoring': [],
            'learning': []
        }
        
        # Task queues by priority
        self.task_queues: Dict[str, deque] = {
            'critical': deque(),   # Execute immediately
            'high': deque(),       # Execute ASAP
            'normal': deque(),     # Execute when available
            'low': deque()         # Execute when idle
        }
        
        # Executors
        self.thread_executor = ThreadPoolExecutor(max_workers=max_workers)
        self.process_executor = ProcessPoolExecutor(max_workers=max(2, max_workers // 2))
        
        # Statistics
        self.total_tasks_submitted = 0
        self.total_tasks_completed = 0
        self.total_tasks_failed = 0
        
        # Initialize workers
        self._spawn_workers()
        
        logger.info(f">> Multi-Model Task Distributor initialized with {max_workers} max workers")
    
    def _spawn_workers(self):
        """Spawn initial workers"""
        # Distribute workers by specialty
        workers_per_specialty = max(1, self.max_workers // 4)
        
        worker_id = 0
        for specialty in ['analysis', 'execution', 'monitoring', 'learning']:
            for _ in range(workers_per_specialty):
                worker = TaskWorker(worker_id, specialty)
                self.workers[specialty].append(worker)
                worker_id += 1
        
        total_workers = sum(len(workers) for workers in self.workers.values())
        logger.info(f"👷 Spawned {total_workers} workers across 4 specialties")
    
    def get_available_worker(self, specialty: str) -> Optional[TaskWorker]:
        """Get an available worker with the right specialty"""
        # First, try to get specialist
        for worker in self.workers[specialty]:
            if not worker.is_busy:
                return worker
        
        # If no specialist available, try any available worker
        for workers_list in self.workers.values():
            for worker in workers_list:
                if not worker.is_busy:
                    logger.debug(f"👷 Using generalist worker {worker.worker_id} for {specialty}")
                    return worker
        
        return None
    
    async def submit_task(
        self,
        function: Callable,
        args: tuple = (),
        kwargs: dict = None,
        priority: str = 'normal',
        specialty: str = 'analysis'
    ) -> asyncio.Future:
        """
        Submit a task for execution
        
        Args:
            function: Function to execute
            args: Positional arguments
            kwargs: Keyword arguments
            priority: 'critical', 'high', 'normal', 'low'
            specialty: 'analysis', 'execution', 'monitoring', 'learning'
            
        Returns:
            Future that will contain the result
        """
        kwargs = kwargs or {}
        
        task = {
            'function': function,
            'args': args,
            'kwargs': kwargs,
            'priority': priority,
            'specialty': specialty,
            'submitted_at': datetime.now()
        }
        
        # Add to queue
        self.task_queues[priority].append(task)
        self.total_tasks_submitted += 1
        
        logger.debug(f"📥 Task submitted: {function.__name__} ({priority}, {specialty})")
        
        # Execute immediately if critical and worker available
        if priority == 'critical':
            return await self._execute_next_task()
        
        # Return future
        future = asyncio.Future()
        return future
    
    async def _execute_next_task(self) -> Optional[Dict]:
        """Execute next task from queue"""
        # Get next task (priority order)
        task = None
        for priority in ['critical', 'high', 'normal', 'low']:
            if self.task_queues[priority]:
                task = self.task_queues[priority].popleft()
                break
        
        if not task:
            return None
        
        # Get available worker
        worker = self.get_available_worker(task['specialty'])
        
        if worker:
            # Execute task
            result = await worker.execute_task(task)
            
            if result['status'] == 'success':
                self.total_tasks_completed += 1
            else:
                self.total_tasks_failed += 1
            
            return result
        else:
            # No worker available, put back in queue
            self.task_queues[task['priority']].appendleft(task)
            logger.debug("⏸️  No worker available, task queued")
            return None
    
    async def process_queue(self, duration_seconds: int = 60):
        """
        Process task queue for specified duration
        
        Args:
            duration_seconds: How long to process tasks
        """
        start_time = datetime.now()
        
        logger.info(f"⚙️  Processing task queue for {duration_seconds}s...")
        
        while (datetime.now() - start_time).seconds < duration_seconds:
            # Process all available tasks
            while True:
                result = await self._execute_next_task()
                if result is None:
                    break
            
            # Brief pause
            await asyncio.sleep(0.1)
        
        logger.info("[OK] Task queue processing complete")
    
    async def parallel_execute(self, tasks: List[Dict]) -> List[Dict]:
        """
        Execute multiple tasks in parallel
        
        Args:
            tasks: List of task dicts with 'function', 'args', 'kwargs'
            
        Returns:
            List of results
        """
        # Submit all tasks
        futures = []
        for task in tasks:
            future = await self.submit_task(
                task['function'],
                task.get('args', ()),
                task.get('kwargs', {}),
                task.get('priority', 'normal'),
                task.get('specialty', 'analysis')
            )
            futures.append(future)
        
        # Wait for all to complete (with timeout)
        results = await asyncio.gather(*[self._execute_next_task() for _ in range(len(tasks))])
        
        return results
    
    def get_load_stats(self) -> Dict:
        """Get current load statistics"""
        busy_workers = sum(
            1 for workers_list in self.workers.values()
            for worker in workers_list
            if worker.is_busy
        )
        
        total_workers = sum(len(workers) for workers in self.workers.values())
        
        queue_sizes = {
            priority: len(queue)
            for priority, queue in self.task_queues.items()
        }
        
        return {
            'total_workers': total_workers,
            'busy_workers': busy_workers,
            'available_workers': total_workers - busy_workers,
            'load_percentage': (busy_workers / total_workers * 100) if total_workers > 0 else 0,
            'queue_sizes': queue_sizes,
            'total_queued': sum(queue_sizes.values()),
            'tasks_submitted': self.total_tasks_submitted,
            'tasks_completed': self.total_tasks_completed,
            'tasks_failed': self.total_tasks_failed,
            'success_rate': (self.total_tasks_completed / self.total_tasks_submitted * 100) if self.total_tasks_submitted > 0 else 0
        }
    
    def get_worker_stats(self) -> Dict:
        """Get worker performance statistics"""
        stats_by_specialty = {}
        
        for specialty, workers_list in self.workers.items():
            stats_by_specialty[specialty] = {
                'count': len(workers_list),
                'busy': sum(1 for w in workers_list if w.is_busy),
                'total_completed': sum(w.tasks_completed for w in workers_list),
                'total_failed': sum(w.tasks_failed for w in workers_list),
                'avg_performance': sum(w.performance_score for w in workers_list) / len(workers_list) if workers_list else 0
            }
        
        return stats_by_specialty
    
    def shutdown(self):
        """Shutdown all executors"""
        self.thread_executor.shutdown(wait=True)
        self.process_executor.shutdown(wait=True)
        logger.info("🛑 Task distributor shutdown complete")


# Global task distributor instance
_task_distributor = None

def get_task_distributor() -> MultiModelTaskDistributor:
    """Get global task distributor instance"""
    global _task_distributor
    if _task_distributor is None:
        _task_distributor = MultiModelTaskDistributor()
    return _task_distributor


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    
    async def test():
        distributor = MultiModelTaskDistributor(max_workers=4)
        
        # Test task functions
        async def analyze_market(symbol: str):
            await asyncio.sleep(0.1)
            return f"Analyzed {symbol}"
        
        async def execute_trade(symbol: str, side: str):
            await asyncio.sleep(0.2)
            return f"Executed {side} on {symbol}"
        
        async def monitor_position(position_id: int):
            await asyncio.sleep(0.05)
            return f"Monitoring position {position_id}"
        
        # Submit tasks
        print("\n" + "="*70)
        print("Submitting tasks:")
        
        tasks = [
            {'function': analyze_market, 'args': ('BTC/USDT',), 'specialty': 'analysis'},
            {'function': analyze_market, 'args': ('ETH/USDT',), 'specialty': 'analysis'},
            {'function': execute_trade, 'args': ('BTC/USDT', 'BUY'), 'specialty': 'execution'},
            {'function': monitor_position, 'args': (1,), 'specialty': 'monitoring'},
            {'function': monitor_position, 'args': (2,), 'specialty': 'monitoring'},
        ]
        
        results = await distributor.parallel_execute(tasks)
        print(f"Results: {results}")
        
        # Stats
        print("\n" + "="*70)
        print("Load stats:", distributor.get_load_stats())
        print("\nWorker stats:", distributor.get_worker_stats())
        
        # Shutdown
        distributor.shutdown()
    
    asyncio.run(test())
