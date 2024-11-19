import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import pytz

from config import MONITORED_LINES, SCHEDULES
from log_config import setup_logging
from tfl_client import TFLClient
from telegram_client import TelegramClient

logger = setup_logging()

class TFLMonitor:
    def __init__(self):
        self.tfl_client = TFLClient()
        self.telegram_client = TelegramClient()
        self.scheduler = AsyncIOScheduler()
        
    async def check_and_notify(self):
        """Main function to check TFL status and send notifications."""
        try:
            logger.info("Starting TFL status check")
            
            # Fetch all line statuses
            statuses = await self.tfl_client.get_all_line_statuses(MONITORED_LINES)
            
            # Send status update via Telegram
            await self.telegram_client.send_status_update(statuses)
            
            logger.info("TFL status check completed successfully")
            
        except Exception as e:
            logger.error(f"Error in check_and_notify: {str(e)}")

    def schedule_jobs(self):
        """Schedule status checks for specified times."""
        london_tz = pytz.timezone('Europe/London')
        
        for schedule in SCHEDULES:
            self.scheduler.add_job(
                self.check_and_notify,
                trigger=CronTrigger(
                    day_of_week='mon-fri',
                    hour=schedule['hour'],
                    minute=schedule['minute'],
                    timezone=london_tz
                ),
                name=f"TFL Status Check {schedule['hour']}:{schedule['minute']:02d}"
            )
            
        logger.info("Scheduled all status check jobs")

    async def startup_check(self):
        """Perform an initial check on startup."""
        logger.info("Performing initial status check on startup")
        await self.check_and_notify()

    def run(self):
        """Start the monitor service."""
        try:
            self.schedule_jobs()
            self.scheduler.start()
            
            # Run initial check
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.startup_check())
            
            # Run the event loop
            loop.run_forever()
            
        except (KeyboardInterrupt, SystemExit):
            logger.info("Shutting down TFL Monitor")
            self.scheduler.shutdown()
        except Exception as e:
            logger.error(f"Error running TFL Monitor: {str(e)}")
            raise

if __name__ == "__main__":
    monitor = TFLMonitor()
    monitor.run()
