import asyncio
from datetime import datetime, timedelta
from typing import Callable, Coroutine, Dict, Any
from config.logger import setup_logger

logger = setup_logger("core.scheduler")

class TaskScheduler:
    def __init__(self):
        logger.info("Initializing Proactive Task Scheduler")
        self.scheduled_tasks: Dict[str, asyncio.Task] = {}
        
    async def schedule_once(self, task_id: str, delay_seconds: int, func: Callable[..., Coroutine], *args: Any, **kwargs: Any) -> None:
        """
        Schedules a one-off task to run after delay_seconds.
        """
        logger.info(f"Scheduling task '{task_id}' to run in {delay_seconds} seconds.")
        
        async def _wrapper():
            await asyncio.sleep(delay_seconds)
            logger.info(f"Executing scheduled task: {task_id}")
            try:
                await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error executing scheduled task '{task_id}': {str(e)}")
            finally:
                if task_id in self.scheduled_tasks:
                    del self.scheduled_tasks[task_id]

        task = asyncio.create_task(_wrapper())
        self.scheduled_tasks[task_id] = task

    async def schedule_recurring(self, task_id: str, interval_seconds: int, func: Callable[..., Coroutine], *args: Any, **kwargs: Any) -> None:
        """
        Schedules a task to run periodically every interval_seconds.
        """
        logger.info(f"Scheduling recurring task '{task_id}' every {interval_seconds} seconds.")
        
        async def _wrapper():
            while True:
                await asyncio.sleep(interval_seconds)
                logger.info(f"Executing recurring task: {task_id}")
                try:
                    await func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error executing recurring task '{task_id}': {str(e)}")

        task = asyncio.create_task(_wrapper())
        self.scheduled_tasks[task_id] = task

    def cancel_task(self, task_id: str) -> bool:
        """
        Cancels a scheduled task.
        """
        if task_id in self.scheduled_tasks:
            self.scheduled_tasks[task_id].cancel()
            del self.scheduled_tasks[task_id]
            logger.info(f"Cancelled task: {task_id}")
            return True
        logger.warning(f"Failed to cancel task '{task_id}': Not found.")
        return False
