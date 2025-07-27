import os
import time
import requests
from telebot import TeleBot
from threading import Thread
from datetime import datetime
import config  # Added import

bot = TeleBot(config.BOT_TOKEN)
ADMIN_ID = "7709001245"
DB_PATH = "users.json"
LOG_FILE = "activity.log"

def log_activity(message: str):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now()}] {message}\n")

def ping_admin():
    while True:
        try:
            bot.send_message(ADMIN_ID, "/start")
            log_activity("Sent keepalive ping")
            time.sleep(300)  # Every 5 minutes
        except Exception as e:
            log_activity(f"Ping failed: {e}")

def backup_db():
    while True:
        try:
            with open(DB_PATH, "rb") as db_file:
                bot.send_document(
                    ADMIN_ID, 
                    db_file, 
                    caption=f"🔄 DB Backup ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
                )
            log_activity("DB backup sent")
            time.sleep(1800)  # Every 30 minutes
        except Exception as e:
            log_activity(f"Backup failed: {e}")

def start_background_tasks():
    Thread(target=ping_admin, daemon=True).start()
    Thread(target=backup_db, daemon=True).start()