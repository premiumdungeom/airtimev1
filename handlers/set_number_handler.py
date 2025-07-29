from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CommandHandler, filters
from database import update_user_number
import re
import asyncio

# State for ConversationHandler
ASK_NUMBER = 1

async def handle_set_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = await context.bot.send_message(
        update.effective_chat.id,
        "📲 <b>Send in your <u>Airtel</u> mobile number:</b>\n\n"
        "⚠️ Make sure it's 11 digits and Airtel ONLY!",
        parse_mode="HTML"
    )
    context.user_data['prompt_message_id'] = prompt.message_id
    return ASK_NUMBER

async def handle_number_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    number = update.message.text.strip()

    # Clean up prompt message
    if 'prompt_message_id' in context.user_data:
        await context.bot.delete_message(user_id, context.user_data['prompt_message_id'])

    if not number.isdigit() or len(number) != 11:
        err = await context.bot.send_message(
            user_id,
            "🥲 <b>Not a valid number</b>. Try again using <b>11 digits</b>.",
            parse_mode="HTML"
        )
        await asyncio.sleep(2)
        await context.bot.delete_message(user_id, err.message_id)
        await context.bot.delete_message(user_id, update.message.message_id)
        return ASK_NUMBER  # Stay in the state

    if not re.match(r"^0(701|702|703|704|705|706|707|708|709|802|808|812|901|902|907|915|919)", number):
        warn = await context.bot.send_message(
            user_id,
            "❌ <b>NOTE:</b> <u>Airtel numbers only</u> are allowed.\n\n"
            "Please tap <b>✅ Set Number</b> again and resend a valid Airtel number.",
            parse_mode="HTML"
        )
        await asyncio.sleep(2)
        await context.bot.delete_message(user_id, warn.message_id)
        await context.bot.delete_message(user_id, update.message.message_id)
        return ConversationHandler.END

    # ✅ Save the number
    update_user_number(user_id, number)

    ok = await context.bot.send_message(
        user_id,
        f"✅ <b>Number saved successfully!</b>\n\n<b>Your Airtel Number:</b> <code>{number}</code>",
        parse_mode="HTML"
    )

    await asyncio.sleep(2)
    await context.bot.delete_message(user_id, ok.message_id)
    await context.bot.delete_message(user_id, update.message.message_id)
    return ConversationHandler.END