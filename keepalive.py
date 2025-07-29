import os
import logging
import asyncio
from datetime import datetime
import config

logger = logging.getLogger(__name__)

ADMIN_ID = config.ADMIN_ID  # Should be an int
DB_PATH = "users.json"
LOG_FILE = "activity.log"

def log_activity(message: str):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now()}] {message}\n")

async def ping_admin_task(bot):
    while True:
        try:
            await bot.send_message(ADMIN_ID, "🫀 Bot heartbeat")
            log_activity("Sent keepalive ping")
        except Exception as e:
            log_activity(f"Ping failed: {e}")
            logger.error(f"Ping failed: {e}")
        await asyncio.sleep(300)  # Every 5 minutes

async def backup_db_task(bot):
    while True:
        try:
            if os.path.exists(DB_PATH):
                with open(DB_PATH, "rb") as db_file:
                    await bot.send_document(
                        ADMIN_ID, 
                        db_file, 
                        caption=f"🔄 DB Backup ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
                    )
                logger.info("DB backup sent")
        except Exception as e:
            logger.error(f"Backup failed: {e}")
        await asyncio.sleep(1800)  # Every 30 minutes

def start_background_tasks(application):
    """
    Start keepalive and backup tasks.
    Call this after PTB Application is built and ready.
    """
    loop = asyncio.get_event_loop()
    bot = application.bot
    loop.create_task(ping_admin_task(bot))
    loop.create_task(backup_db_task(bot))