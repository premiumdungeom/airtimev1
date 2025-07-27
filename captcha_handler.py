#utils/captcha_handler.py
from flask import jsonify, request
import requests
from config import CAPTCHA_API_KEY, ADMIN_ID
from database import block_user, update_user
from telebot import TeleBot

def verify_captcha_result(user_id: int, bot: TeleBot) -> bool:
    """
    Check if user passed captcha by querying your API
    Returns True if verified, False if blocked
    """
    try:
        # Call your captcha API internally
        api_url = f"{config.CAPTCHA_API_URL}?user_id={user_id}"
        response = requests.get(api_url).json()

        if response.get("flags", {}).get("vpn"):
            bot.send_message(ADMIN_ID, f"🚨 VPN User Blocked: {user_id}")
            block_user(user_id)
            return False

        if response.get("flags", {}).get("multi_account"):
            bot.send_message(ADMIN_ID, f"🚨 Multi-Account Blocked: {user_id}")
            block_user(user_id)
            return False

        # Mark as verified in DB
        update_user(user_id, {"verified": True})
        return True

    except Exception as e:
        bot.send_message(ADMIN_ID, f"⚠️ Captcha Error: {str(e)}")
        return False

# Webhook handler (for your captcha app)
def process_captcha(bot: TeleBot, data: dict):
    # Verify secret key
    if data.get("api_key") != CAPTCHA_API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = data["user_id"]
    flags = data.get("flags", {})

    # Auto-ban logic
    if flags.get("vpn") or flags.get("multi_account"):
        block_user(user_id)
        bot.send_message(
            user_id,
            "🚫 <b>ACCESS DENIED</b>\n"
            "VPN/Multi-Account detected.\n"
            "Contact admin if this is a mistake."
        )
        return jsonify({"status": "banned"})

    # Successful verification
    update_user(user_id, {"verified": True})
    bot.send_message(
        user_id,
        "✅ <b>VERIFIED!</b>\n"
        "You can now use all bot features.",
        reply_markup=main_menu_keyboard()  # Your existing menu
    )
    return jsonify({"status": "verified"})