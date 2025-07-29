from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from database import get_user, increment_balance
from config import CHANNEL_USERNAME  # No need for BOT_TOKEN here
import asyncio

async def handle_claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    user = get_user(user_id)

    if not user.get("number"):
        warn = await context.bot.send_message(
            user_id,
            "📲 You haven't set a number yet.\nTap <b>✅ Set Number</b> to add your Airtel number.",
            parse_mode="HTML"
        )
        await asyncio.sleep(2)
        await context.bot.delete_message(user_id, warn.message_id)
        return

    if user.get("balance", 0) < 100:
        err = await context.bot.send_message(
            user_id,
            "😓 You need at least ₦100 to claim.",
            parse_mode="HTML"
        )
        await asyncio.sleep(2)
        await context.bot.delete_message(user_id, err.message_id)
        return

    claim_type = "airtime" if "Airtime" in update.message.text else "data"
    await process_claim(update, context, user, claim_type)

async def process_claim(update: Update, context: ContextTypes.DEFAULT_TYPE, user, claim_type: str):
    user_id = update.effective_chat.id
    username = f"@{update.effective_user.username}" if update.effective_user.username else f"<code>{user_id}</code>"

    amount = user.get("balance", 0)
    network = "Airtel"
    number = user.get("number")

    # Deduct balance
    increment_balance(user_id, 0)

    # Send to channel
    bot_username = (await context.bot.get_me()).username
    text = (
        f"💸 <b>New Withdrawal Request</b>\n\n"
        f"👤 <b>User:</b> {username}\n"
        f"📞 <b>Number:</b> <code>{number}</code>\n"
        f"💰 <b>Amount:</b> {amount} {'MB' if claim_type == 'data' else '₦'}\n"
        f"📡 <b>Network:</b> {network}\n"
        f"⚙️ <b>Status:</b> Processing\n"
        f"🤖 <b>BOT:</b> <a href='https://t.me/{bot_username}'>Link</a>"
    )

    await context.bot.send_message(CHANNEL_USERNAME, text, parse_mode="HTML")

    # Confirm to user
    confirm = await context.bot.send_message(
        user_id,
        "✅ <b>Your claim has been submitted and is being processed!</b>\n"
        "Expect delivery shortly.",
        parse_mode="HTML"
    )
    await asyncio.sleep(2)
    await context.bot.delete_message(user_id, confirm.message_id)
    await context.bot.delete_message(user_id, update.message.message_id)