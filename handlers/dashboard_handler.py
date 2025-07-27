#handlers/dashboard_handler.py
from telebot.types import Message
from database import get_user_data, get_user_ref_link
from config import REF_BONUS_AMOUNT, REF_BONUS_MB
import time

def handle_dashboard(bot, message: Message):  # Changed to use passed bot instance
    user_id = message.chat.id
    user_data = get_user_data(user_id)

    # Fallback if user doesn't exist
    if not user_data:
        bot.send_message(user_id, "👤 User not found. Please /start first.")
        return

    balance_naira = user_data.get("balance_naira", 0)
    balance_mb = int(balance_naira * 0.75)
    ref_link = get_user_ref_link(user_id)

    # Dashboard message
    msg = (
        f"📊 <b>DASHBOARD</b>\n\n"
        f"💰 <b>Balance:</b> N{balance_naira:.2f} Airtime or {balance_mb}MB\n\n"
        f"👥 <b>Per Invite:</b> N{REF_BONUS_AMOUNT} or {REF_BONUS_MB}MB\n"
        f"📢 <b>Invite Friends to Earn More Airtime!</b>\n\n"
        f"🔗 <b>Invite Link:</b>\n<code>{ref_link}</code>"
    )

    sent = bot.send_message(user_id, msg, parse_mode="HTML")

    # Auto-delete both dashboard and user's tap message
    time.sleep(2)
    bot.delete_message(user_id, sent.message_id)
    bot.delete_message(user_id, message.message_id)