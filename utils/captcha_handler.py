from flask import jsonify, request
import requests
from config import CAPTCHA_API_KEY, ADMIN_ID, CAPTCHA_API_URL
from database import block_user, update_user
from handlers.mainmenu_handler import build_main_menu_keyboard  # You need to provide this as an async function
import asyncio

# Async version for use with python-telegram-bot
async def verify_captcha_result(user_id: int, bot) -> bool:
    """
    Check if user passed captcha by querying your API
    Returns True if verified, False if blocked
    """
    try:
        api_url = f"{CAPTCHA_API_URL}?user_id={user_id}"
        response = requests.get(api_url).json()

        if response.get("flags", {}).get("vpn"):
            await bot.send_message(ADMIN_ID, f"🚨 VPN User Blocked: {user_id}")
            block_user(user_id)
            return False

        if response.get("flags", {}).get("multi_account"):
            await bot.send_message(ADMIN_ID, f"🚨 Multi-Account Blocked: {user_id}")
            block_user(user_id)
            return False

        # Mark as verified in DB
        update_user(user_id, {"verified": True})
        return True

    except Exception as e:
        await bot.send_message(ADMIN_ID, f"⚠️ Captcha Error: {str(e)}")
        return False

# Flask webhook handler (synchronous, but calls async Telegram code)
def process_captcha(bot, data: dict):
    if data.get("api_key") != CAPTCHA_API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = data["user_id"]
    flags = data.get("flags", {})

    # Auto-ban logic
    if flags.get("vpn") or flags.get("multi_account"):
        block_user(user_id)
        asyncio.run(
            bot.send_message(
                user_id,
                "🚫 <b>ACCESS DENIED</b>\n"
                "VPN/Multi-Account detected.\n"
                "Contact admin if this is a mistake.",
                parse_mode="HTML"
            )
        )
        return jsonify({"status": "banned"})

    # Successful verification
    update_user(user_id, {"verified": True})
    asyncio.run(
        bot.send_message(
            user_id,
            "✅ <b>VERIFIED!</b>\n"
            "You can now use all bot features.",
            reply_markup=build_main_menu_keyboard(),  # <-- make sure this is an InlineKeyboardMarkup or ReplyKeyboardMarkup
            parse_mode="HTML"
        )
    )
    return jsonify({"status": "verified"})