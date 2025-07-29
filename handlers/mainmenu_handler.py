from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import ContextTypes
from config import FIRE_STICKER_ID
import asyncio

def build_main_menu_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("👏 Dashboard")],
            [KeyboardButton("📱 Claim as Airtime"), KeyboardButton("📡 Claim as Data")],
            [KeyboardButton("✅ Set Number")]
        ],
        resize_keyboard=True
    )

async def handle_mainmenu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id

    # 🔥 Sticker
    await context.bot.send_sticker(user_id, FIRE_STICKER_ID)

    # Menu text
    menu_text = "🔥"

    # Keyboard
    menu = build_main_menu_keyboard()

    # Send menu
    sent = await context.bot.send_message(user_id, menu_text, reply_markup=menu)

    # Auto-delete after 2 seconds
    await asyncio.sleep(2)
    await context.bot.delete_message(user_id, sent.message_id)
    await context.bot.delete_message(user_id, update.message.message_id)