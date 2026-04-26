# src/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from typing import Callable, Optional
import logging
from logging_utils import logger

class TaskScheduler:
    """Manage background scheduled tasks"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.jobs = {}
    
    def add_interval_job(
        self,
        func: Callable,
        minutes: int = 5,
        job_id: str = None,
        args: tuple = None,
        kwargs: dict = None
    ):
        """Add a job that runs at regular intervals"""
        
        job_id = job_id or func.__name__
        
        try:
            job = self.scheduler.add_job(
                func,
                'interval',
                minutes=minutes,
                id=job_id,
                args=args or (),
                kwargs=kwargs or {},
                replace_existing=True,
                misfire_grace_time=60
            )
            
            self.jobs[job_id] = job
            logger.info(f"✅ Added interval job: {job_id} (every {minutes}m)")
            
            return job
        
        except Exception as e:
            logger.error(f"❌ Error adding job: {e}")
            return None
    
    def add_cron_job(
        self,
        func: Callable,
        hour: int = 0,
        minute: int = 0,
        job_id: str = None,
        args: tuple = None,
        kwargs: dict = None
    ):
        """Add a job that runs at specific times (cron-style)"""
        
        job_id = job_id or func.__name__
        
        try:
            job = self.scheduler.add_job(
                func,
                'cron',
                hour=hour,
                minute=minute,
                id=job_id,
                args=args or (),
                kwargs=kwargs or {},
                replace_existing=True
            )
            
            self.jobs[job_id] = job
            logger.info(f"✅ Added cron job: {job_id} ({hour:02d}:{minute:02d})")
            
            return job
        
        except Exception as e:
            logger.error(f"❌ Error adding cron job: {e}")
            return None
    
    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("✅ Task scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("✅ Task scheduler stopped")
    
    def list_jobs(self):
        """List all scheduled jobs"""
        jobs = self.scheduler.get_jobs()
        logger.info(f"📋 Scheduled jobs: {len(jobs)}")
        for job in jobs:
            logger.info(f"   - {job.id}: {job.trigger}")
    
    def remove_job(self, job_id: str):
        """Remove a scheduled job"""
        try:
            self.scheduler.remove_job(job_id)
            if job_id in self.jobs:
                del self.jobs[job_id]
            logger.info(f"✅ Removed job: {job_id}")
        except Exception as e:
            logger.error(f"❌ Error removing job: {e}")
