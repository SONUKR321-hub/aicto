"""Scheduling functionality for automated posting"""

import logging
from datetime import datetime, time
from typing import Callable, List
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

class Scheduler:
    """Handles scheduling of posts"""
    
    def __init__(self, config):
        self.config = config
        self.scheduler = BackgroundScheduler()
        self.timezone = pytz.timezone(config.get('schedule.timezone', 'UTC'))
        
    def start(self):
        """Start the scheduler"""
        if not self.config.get('schedule.enabled', True):
            logger.info("Scheduling is disabled")
            return
        
        logger.info("Starting scheduler")
        self.scheduler.start()
    
    def stop(self):
        """Stop the scheduler"""
        logger.info("Stopping scheduler")
        self.scheduler.shutdown()
    
    def schedule_posts(self, post_function: Callable):
        """
        Schedule posts based on configuration
        post_function: Function to call when it's time to post
        """
        frequency = self.config.get('schedule.frequency', 'daily')
        post_times = self.config.get('schedule.post_times', ['19:00'])
        
        logger.info(f"Scheduling posts: {frequency} at {post_times}")
        
        for post_time_str in post_times:
            hour, minute = self._parse_time(post_time_str)
            
            if frequency == 'daily':
                trigger = CronTrigger(
                    hour=hour,
                    minute=minute,
                    timezone=self.timezone
                )
                self.scheduler.add_job(
                    post_function,
                    trigger=trigger,
                    id=f'daily_post_{hour}_{minute}',
                    replace_existing=True
                )
                logger.info(f"Scheduled daily post at {hour:02d}:{minute:02d}")
            
            elif frequency == 'twice_daily':
                # Morning and evening posts
                trigger1 = CronTrigger(hour=9, minute=0, timezone=self.timezone)
                trigger2 = CronTrigger(hour=19, minute=0, timezone=self.timezone)
                
                self.scheduler.add_job(
                    post_function,
                    trigger=trigger1,
                    id='morning_post',
                    replace_existing=True
                )
                self.scheduler.add_job(
                    post_function,
                    trigger=trigger2,
                    id='evening_post',
                    replace_existing=True
                )
                logger.info("Scheduled twice daily posts (9 AM and 7 PM)")
    
    def schedule_analytics_update(self, update_function: Callable):
        """Schedule periodic analytics updates"""
        if not self.config.get('analytics.enabled', True):
            return
        
        # Update analytics every hour
        trigger = CronTrigger(minute=0, timezone=self.timezone)
        self.scheduler.add_job(
            update_function,
            trigger=trigger,
            id='analytics_update',
            replace_existing=True
        )
        logger.info("Scheduled hourly analytics updates")
    
    def schedule_one_time_post(self, post_function: Callable, post_time: datetime):
        """Schedule a one-time post"""
        self.scheduler.add_job(
            post_function,
            trigger='date',
            run_date=post_time,
            timezone=self.timezone
        )
        logger.info(f"Scheduled one-time post at {post_time}")
    
    def get_scheduled_jobs(self) -> List[dict]:
        """Get list of scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        return jobs
    
    def remove_job(self, job_id: str):
        """Remove a scheduled job"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed job: {job_id}")
        except Exception as e:
            logger.error(f"Error removing job: {e}")
    
    def _parse_time(self, time_str: str) -> tuple:
        """Parse time string (HH:MM) to hour and minute"""
        try:
            hour, minute = time_str.split(':')
            return int(hour), int(minute)
        except Exception as e:
            logger.error(f"Error parsing time '{time_str}': {e}")
            return 19, 0  # Default to 7 PM
    
    def is_running(self) -> bool:
        """Check if scheduler is running"""
        return self.scheduler.running
