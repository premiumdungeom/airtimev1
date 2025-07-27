from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import REQUIRED_CHANNELS, CAPTCHA_WEBAPP_URL
from utils.check_join import check_user_joined

def send_welcome_screen(bot, user_id):
    """Text-only welcome screen with channels"""
    welcome_text = (
        "<b>👋 Welcome!</b>\n"
        "Get free Airtime and Data 🔥 by inviting friends.\n\n"
        "📢 <b>Join all channels to continue:</b>\n\n"
        + "\n".join([f"➡️ <a href='https://t.me/{ch}'>@{ch}</a>" for ch in REQUIRED_CHANNELS]) +
        "\n\nThen tap <b>Proceed ✅</b>."
    )

    keyboard = InlineKeyboardMarkup()
    for ch in REQUIRED_CHANNELS:
        keyboard.add(InlineKeyboardButton(text=f"🔗 @{ch}", url=f"https://t.me/{ch}"))
    keyboard.add(InlineKeyboardButton("✅ Proceed", callback_data="check_joined"))

    # Send text message with buttons instead of photo
    bot.send_message(
        user_id,
        welcome_text,
        reply_markup=keyboard,
        parse_mode="HTML",
        disable_web_page_preview=True
    )

def handle_start(bot, message):
    try:
        user_id = message.from_user.id
        logger.info(f"Processing /start for {user_id}")
        
        # Verify bot can send messages
        test_msg = bot.send_message(user_id, "🔄 Starting...")
        bot.delete_message(user_id, test_msg.message_id)
        
        send_welcome_screen(bot, user_id)
    except Exception as e:
        logger.error(f"Start failed: {str(e)}")
        bot.reply_to(message, "⚠️ Bot error - please try later")

def setup_start_handlers(bot):
    @bot.callback_query_handler(func=lambda call: call.data == "check_joined")
    def callback_check_joined(call):
        user_id = call.from_user.id
        
        if not check_user_joined(user_id):
            bot.answer_callback_query(call.id, "❌ Join all channels first!")
            return
        
        # ✅ User joined channels - now show CAPTCHA
        captcha_url = f"{CAPTCHA_WEBAPP_URL}?user_id={user_id}"
        
        bot.send_message(
            user_id,
            "🔐 <b>Final Verification</b>\n"
            "Prove you're human to continue:",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton(
                    "⚠️ Verify Human", 
                    web_app={"url": captcha_url}
                )
            )
        )