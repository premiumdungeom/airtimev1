from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import REQUIRED_CHANNELS, CAPTCHA_WEBAPP_URL
from utils.check_join import check_user_joined
from database import create_user, is_blocked
import logging

logger = logging.getLogger(__name__)

def send_welcome_screen(bot, user_id):
    """
    Sends text-only welcome message with channel links
    """
    try:
        welcome_text = (
            "<b>👋 Welcome!</b>\n"
            "Get free Airtime and Data 🔥 by inviting friends.\n\n"
            "📢 <b>Join all channels to continue:</b>\n\n"
            + "\n".join([f"➡️ <a href='https://t.me/{ch}'>@{ch}</a>" for ch in REQUIRED_CHANNELS]) +
            "\n\nThen tap <b>Proceed ✅</b>."
        )

        keyboard = InlineKeyboardMarkup()
        for ch in REQUIRED_CHANNELS:
            keyboard.add(InlineKeyboardButton(
                text=f"🔗 @{ch}", 
                url=f"https://t.me/{ch}"
            ))
        keyboard.add(InlineKeyboardButton(
            "✅ Proceed", 
            callback_data="check_joined"
        ))

        bot.send_message(
            user_id,
            welcome_text,
            reply_markup=keyboard,
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        logger.info(f"Sent welcome screen to {user_id}")
        
    except Exception as e:
        logger.error(f"Welcome screen failed for {user_id}: {str(e)}")
        raise

def handle_start(bot, message):
    """
    Handles /start command with referrer tracking
    """
    try:
        user_id = message.from_user.id
        if is_blocked(user_id):
            bot.send_message(user_id, "🚫 Access Denied")
            return

        logger.info(f"Processing /start from {user_id}")
        
        # Handle referrer if exists
        referrer_id = None
        if len(message.text.split()) > 1:
            try:
                referrer_id = int(message.text.split()[1])
                logger.info(f"Referral detected from {referrer_id}")
            except ValueError:
                pass

        # Create user and show welcome
        create_user(user_id, referrer_id)
        send_welcome_screen(bot, user_id)

    except Exception as e:
        logger.error(f"Start handler crashed: {str(e)}")
        bot.reply_to(message, "⚠️ Bot error - please try again")

def setup_start_handlers(bot):
    """
    Registers all start-related handlers
    """
    @bot.message_handler(commands=['start'])
    def start_wrapper(message):
    logger.info(f"Received /start from {message.from_user.id}")
    handle_start(bot, message)

    @bot.callback_query_handler(func=lambda call: call.data == "check_joined")
    def callback_check_joined(call):
        try:
            user_id = call.from_user.id
            logger.info(f"Checking channels for {user_id}")
            
            if not check_user_joined(user_id):
                bot.answer_callback_query(
                    call.id, 
                    "❌ Join all channels first!"
                )
                return
            
            # Show CAPTCHA after channel verification
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
                ),
                parse_mode="HTML"
            )
            logger.info(f"CAPTCHA shown to {user_id}")
            
        except Exception as e:
            logger.error(f"Callback failed: {str(e)}")
            bot.answer_callback_query(
                call.id,
                "⚠️ System error - try again"
            )

    logger.info("✅ Start handlers registered successfully")