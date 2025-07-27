#handlers/set_number_handler.py 
from telebot.types import Message
from database import update_user_number
import re
import time

def handle_set_number(bot, message: Message):  # Changed to use passed bot instance
    prompt = bot.send_message(
        message.chat.id,
        "📲 <b>Send in your <u>Airtel</u> mobile number:</b>\n\n"
        "⚠️ Make sure it's 11 digits and Airtel ONLY!",
        parse_mode="HTML"
    )
    bot.register_next_step_handler(prompt, lambda msg: handle_number_input(bot, msg))

def handle_number_input(bot, message: Message):  # Added bot parameter
    user_id = message.chat.id
    number = message.text.strip()

    if not number.isdigit() or len(number) != 11:
        err = bot.send_message(
            user_id,
            "🥲 <b>Not a valid number</b>. Try again using <b>11 digits</b>.",
            parse_mode="HTML"
        )
        time.sleep(2)
        bot.delete_message(user_id, err.message_id)
        bot.delete_message(user_id, message.message_id)
        return

    if not re.match(r"^0(701|702|703|704|705|706|707|708|709|802|808|812|901|902|907|915|919)", number):
        warn = bot.send_message(
            user_id,
            "❌ <b>NOTE:</b> <u>Airtel numbers only</u> are allowed.\n\n"
            "Please tap <b>✅ Set Number</b> again and resend a valid Airtel number.",
            parse_mode="HTML"
        )
        time.sleep(2)
        bot.delete_message(user_id, warn.message_id)
        bot.delete_message(user_id, message.message_id)
        return

    # ✅ Save the number
    update_user_number(user_id, number)

    ok = bot.send_message(
        user_id,
        f"✅ <b>Number saved successfully!</b>\n\n<b>Your Airtel Number:</b> <code>{number}</code>",
        parse_mode="HTML"
    )

    time.sleep(2)
    bot.delete_message(user_id, ok.message_id)
    bot.delete_message(user_id, message.message_id)
