from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from config import REQUIRED_CHANNELS, CAPTCHA_WEBAPP_URL
from utils.check_join import check_user_joined
from database import create_user, is_blocked
import logging

logger = logging.getLogger(__name__)

def build_welcome_keyboard():
    keyboard = [
        [InlineKeyboardButton(f"🔗 @{ch}", url=f"https://t.me/{ch}")]
        for ch in REQUIRED_CHANNELS
    ]
    keyboard.append([InlineKeyboardButton("✅ Proceed", callback_data="check_joined")])
    return InlineKeyboardMarkup(keyboard)

async def send_welcome_screen(context: ContextTypes.DEFAULT_TYPE, user_id):
    try:
        welcome_text = (
            "<b>👋 Welcome!</b>\n"
            "Get free Airtime and Data 🔥 by inviting friends.\n\n"
            "📢 <b>Join all channels to continue:</b>\n\n"
            + "\n".join([f"➡️ <a href='https://t.me/{ch}'>@{ch}</a>" for ch in REQUIRED_CHANNELS]) +
            "\n\nThen tap <b>Proceed ✅</b>."
        )
        await context.bot.send_message(
            user_id,
            welcome_text,
            reply_markup=build_welcome_keyboard(),
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        logger.info(f"Sent welcome screen to {user_id}")
    except Exception as e:
        logger.error(f"Welcome screen failed for {user_id}: {str(e)}")
        raise

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        if is_blocked(user_id):
            await context.bot.send_message(user_id, "🚫 Access Denied")
            return

        logger.info(f"Processing /start from {user_id}")

        referrer_id = None
        args = context.args if hasattr(context, "args") else []
        if args:
            try:
                referrer_id = int(args[0])
                logger.info(f"Referral detected from {referrer_id}")
            except ValueError:
                pass

        create_user(user_id, referrer_id)
        await send_welcome_screen(context, user_id)

    except Exception as e:
        logger.error(f"Start handler crashed: {str(e)}")
        if update.message:
            await update.message.reply_text("⚠️ Bot error - please try again")

async def callback_check_joined(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        user_id = query.from_user.id
        logger.info(f"Checking channels for {user_id}")

        if not await check_user_joined(context.bot, user_id):
            await query.answer("❌ Join all channels first!", show_alert=True)
            return

        captcha_url = f"{CAPTCHA_WEBAPP_URL}?user_id={user_id}"
        await context.bot.send_message(
            user_id,
            "🔐 <b>Final Verification</b>\n"
            "Prove you're human to continue:",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("⚠️ Verify Human", web_app={"url": captcha_url})]]
            ),
            parse_mode="HTML"
        )
        await query.answer()
        logger.info(f"CAPTCHA shown to {user_id}")

    except Exception as e:
        logger.error(f"Callback failed: {str(e)}")
        await update.callback_query.answer("⚠️ System error - try again", show_alert=True)