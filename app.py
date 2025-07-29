import logging
import os
from flask import Flask, request, jsonify

from telegram import Update
from telegram.ext import (
    Application, ApplicationBuilder,
    CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler
)

import config
from keepalive import start_background_tasks
from database import create_user, is_blocked, block_user, get_user, update_user
from utils.check_join import check_user_joined
from utils.referral import handle_referral
from utils.captcha_handler import process_captcha
from handlers.start_handler import handle_start, callback_check_joined
from handlers.mainmenu_handler import handle_mainmenu, build_main_menu_keyboard
from handlers.set_number_handler import handle_set_number, handle_number_input, ASK_NUMBER
from handlers.dashboard_handler import handle_dashboard
from handlers.claim_handler import handle_claim

# Logging setup
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Flask app
app = Flask(__name__)

# Global state
application: Application = None  # Will be set after building the PTB application

def initialize_bot():
    global application
    logger.info("Initializing bot services...")

    # 1. Build PTB application FIRST
    application = (
        ApplicationBuilder()
        .token(config.BOT_TOKEN)
        .concurrent_updates(True)
        .build()
    )

    # 2. Start background tasks, passing in the application
    start_background_tasks(application)

    # 3. Register handlers
    application.add_handler(CommandHandler("start", handle_start))
    application.add_handler(CallbackQueryHandler(callback_check_joined, pattern="^check_joined$"))
    application.add_handler(MessageHandler(filters.Regex("^👏 Dashboard$"), handle_dashboard))
    application.add_handler(MessageHandler(filters.Regex("^✅ Set Number$"), handle_set_number))
    # Conversation for entering number
    application.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^✅ Set Number$"), handle_set_number)],
        states={ASK_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_number_input)]},
        fallbacks=[],
    ))
    application.add_handler(MessageHandler(filters.Regex("^🏠 Main Menu$"), handle_mainmenu))
    application.add_handler(MessageHandler(filters.Regex("^📱 Claim as Airtime$"), handle_claim))
    application.add_handler(MessageHandler(filters.Regex("^📡 Claim as Data$"), handle_claim))
    # Add more handlers as needed

    # 4. Set webhook
    webhook_url = f"{config.WEBHOOK_URL}/{config.BOT_TOKEN}"
    application.bot.set_webhook(
        url=webhook_url,
        allowed_updates=["message", "callback_query"],
        secret_token=config.WEBHOOK_SECRET
    )
    logger.info("✅ Bot initialization complete")

# Flask webhook endpoint
@app.route(f'/{config.BOT_TOKEN}', methods=['POST'])
def telegram_webhook():
    """Receive updates from Telegram and pass to PTB Application."""
    if request.headers.get('X-Telegram-Bot-Api-Secret-Token') != config.WEBHOOK_SECRET:
        logger.warning("⚠️ Unauthorized webhook access attempt")
        return "Unauthorized", 403

    try:
        update_json = request.get_data(as_text=True)
        update = Update.de_json(update_json, application.bot)
        application.update_queue.put_nowait(update)
        return "ok", 200
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        return "error", 500

# Health endpoints
@app.route('/debug')
def debug():
    try:
        bot_info = application.bot.get_me()
        webhook_info = application.bot.get_webhook_info()
        return jsonify({
            "bot_ready": bool(bot_info),
            "webhook_url": webhook_info.url,
            "pending_updates": webhook_info.pending_update_count,
            "handlers_registered": True
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health_check():
    try:
        webhook_info = application.bot.get_webhook_info()
        return jsonify({
            "status": "running",
            "webhook_set": bool(webhook_info.url),
            "last_error": None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/start', methods=['GET', 'POST'])
def start():
    return "Bot is live ✅"

@app.route('/captcha_webhook', methods=['POST'])
def captcha_webhook():
    if request.headers.get('X-API-KEY') != config.CAPTCHA_API_KEY:
        return jsonify({"error": "Invalid key"}), 403
        
    data = request.get_json()
    # For security, you may want to check request.remote_addr
    # if request.remote_addr not in ["76.76.21.21", "::1"]:
    #     return jsonify({"error": "Invalid source"}), 403

    try:
        user_id = data.get('user_id')
        captcha_result = data.get('result')
        if not user_id or not captcha_result:
            return jsonify({"error": "Missing data"}), 400

        # process_captcha must be adapted to PTB async if you want to await it
        bot = application.bot
        success = process_captcha(bot, data)
        return jsonify({
            "success": success,
            "message": "Captcha verified" if success else "Verification failed"
        }), 200 if success else 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Start everything
initialize_bot()

if __name__ == '__main__':
    port = 10000
    app.run(host='0.0.0.0', port=port)