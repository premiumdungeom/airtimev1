from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import REQUIRED_CHANNELS, CAPTCHA_WEBAPP_URL
from utils.check_join import is_user_joined_all
from telebot import TeleBot

def send_welcome_screen(user_id):
    """Your EXACT welcome screen with channels"""
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

    with open("templates/welcome.jpg", "rb") as img:
        bot.send_photo(user_id, img, caption=welcome_text, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "check_joined")
def callback_check_joined(call):
    user_id = call.from_user.id
    
    if not is_user_joined_all(user_id):
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
