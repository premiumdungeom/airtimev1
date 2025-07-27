#handlers/claim_handler.py
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from telebot import TeleBot
from database import get_user, update_user_balance
import time

bot = TeleBot("YOUR_BOT_TOKEN", parse_mode="HTML")
CHANNEL_USERNAME = "@combohamsterdailys"  # Update with your channel username


@bot.message_handler(func=lambda m: m.text == "📤 Claim as Airtime" or m.text == "📶 Claim as Data")
def handle_claim_type(message: Message):
    user = get_user(message.chat.id)

    if not user.get("number"):
        warn = bot.send_message(
            message.chat.id,
            "📲 You haven't set a number yet.\nTap <b>✅ Set Number</b> to add your Airtel number."
        )
        time.sleep(2)
        bot.delete_message(message.chat.id, warn.message_id)
        return

    if user.get("balance", 0) < 100:
        err = bot.send_message(
            message.chat.id,
            "😓 You need at least ₦100 to claim."
        )
        time.sleep(2)
        bot.delete_message(message.chat.id, err.message_id)
        return

    claim_type = "airtime" if "Airtime" in message.text else "data"
    process_claim(message, user, claim_type)


def process_claim(message: Message, user, claim_type: str):
    user_id = message.chat.id
    username = f"@{message.from_user.username}" if message.from_user.username else f"<code>{user_id}</code>"

    amount = user.get("balance", 0)
    network = "Airtel"
    number = user.get("number")

    # Deduct balance
    update_user_balance(user_id, 0)

    # Send to channel
    text = (
        f"💸 <b>New Withdrawal Request</b>\n\n"
        f"👤 <b>User:</b> {username}\n"
        f"📞 <b>Number:</b> <code>{number}</code>\n"
        f"💰 <b>Amount:</b> {amount} {'MB' if claim_type == 'data' else '₦'}\n"
        f"📡 <b>Network:</b> {network}\n"
        f"⚙️ <b>Status:</b> Processing\n"
        f"🤖 <b>BOT:</b> <a href='https://t.me/{bot.get_me().username}'>Link</a>"
    )

    bot.send_message(CHANNEL_USERNAME, text)

    # Confirm to user
    confirm = bot.send_message(
        user_id,
        "✅ <b>Your claim has been submitted and is being processed!</b>\n"
        "Expect delivery shortly."
    )
    time.sleep(2)
    bot.delete_message(user_id, confirm.message_id)
    bot.delete_message(user_id, message.message_id)
