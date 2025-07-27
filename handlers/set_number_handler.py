#handlers/set_number_handler.py 
from telebot.types import Message
from telebot import TeleBot
from database import update_user_number
import re
import time

bot = TeleBot("YOUR_BOT_TOKEN", parse_mode="HTML")  # Or import bot from app.py

# Step 1: Trigger by button
@bot.message_handler(func=lambda m: m.text == "✅ Set Number")
def ask_for_number(message: Message):
    prompt = bot.send_message(
        message.chat.id,
        "📲 <b>Send in your <u>Airtel</u> mobile number:</b>\n\n"
        "⚠️ Make sure it's 11 digits and Airtel ONLY!"
    )
    bot.register_next_step_handler(prompt, handle_number_input)


# Step 2: Handle and validate
def handle_number_input(message: Message):
    user_id = message.chat.id
    number = message.text.strip()

    if not number.isdigit() or len(number) != 11:
        err = bot.send_message(
            user_id,
            "🥲 <b>Not a valid number</b>. Try again using <b>11 digits</b>."
        )
        time.sleep(2)
        bot.delete_message(user_id, err.message_id)
        bot.delete_message(user_id, message.message_id)
        return

    if not re.match(r"^0(701|702|703|704|705|706|707|708|709|802|808|812|901|902|907|915|919)", number):
        warn = bot.send_message(
            user_id,
            "❌ <b>NOTE:</b> <u>Airtel numbers only</u> are allowed.\n\n"
            "Please tap <b>✅ Set Number</b> again and resend a valid Airtel number."
        )
        time.sleep(2)
        bot.delete_message(user_id, warn.message_id)
        bot.delete_message(user_id, message.message_id)
        return

    # ✅ Save the number
    update_user_number(user_id, number)

    ok = bot.send_message(
        user_id,
        f"✅ <b>Number saved successfully!</b>\n\n<b>Your Airtel Number:</b> <code>{number}</code>"
    )

    time.sleep(2)
    bot.delete_message(user_id, ok.message_id)
    bot.delete_message(user_id, message.message_id)
