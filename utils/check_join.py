#utils/check_join.py
import telebot
from config import BOT_TOKEN, REQUIRED_CHANNELS

bot = telebot.TeleBot(BOT_TOKEN)

def check_user_joined(user_id: int) -> bool:
    for channel in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ['left', 'kicked']:
                return False
        except Exception as e:
            print(f"Error checking channel {channel}: {e}")
            return False
    return True