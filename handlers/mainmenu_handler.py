#handlers/mainmenu_handler.py
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, Message
from config import FIRE_STICKER_ID
import time

def handle_mainmenu(bot, message: Message):  # Add bot parameter
    user_id = message.chat.id

    # 🔥 Sticker
    bot.send_sticker(user_id, FIRE_STICKER_ID)

    # Menu text
    menu_text = "🔥"

    # Keyboard
    menu = ReplyKeyboardMarkup(resize_keyboard=True)
    menu.row(KeyboardButton("👏 Dashboard"))
    menu.row(KeyboardButton("📱 Claim as Airtime"), KeyboardButton("📡 Claim as Data"))
    menu.row(KeyboardButton("✅ Set Number"))

    # Send menu
    sent = bot.send_message(user_id, menu_text, reply_markup=menu)

    # Auto-delete after 2 seconds
    time.sleep(2)
    bot.delete_message(user_id, sent.message_id)
    bot.delete_message(user_id, message.message_id)