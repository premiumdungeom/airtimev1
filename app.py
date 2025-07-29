from flask import Flask, request, jsonify
import telebot
import config
import logging
from keepalive import start_background_tasks, ADMIN_ID, DB_PATH
from database import create_user, is_blocked, block_user, get_user, update_user
from utils.check_join import check_user_joined
from utils.referral import handle_referral
from utils.captcha_handler import process_captcha
from handlers.start_handler import handle_start, setup_start_handlers
from handlers.mainmenu_handler import handle_mainmenu
from handlers.dashboard_handler import handle_dashboard
from handlers.set_number_handler import handle_set_number
from handlers.claim_handler import handle_claim

# Initialize logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Global variables
webhook_initialized = False
last_error = None

app = Flask(__name__)
bot = telebot.TeleBot(config.BOT_TOKEN, skip_pending=True, threaded=True)

# Verify bot token works
try:
    bot_info = bot.get_me()
    logger.info(f"Bot authorized as @{bot_info.username}")
except Exception as e:
    logger.error(f"Bot auth failed: {e}")
    raise

# Initialize everything
def initialize_bot():
    try:
        logger.info("Initializing bot services...")
        
        # 1. Start background tasks
        start_background_tasks()
        
        # 2. Register all handlers
        setup_start_handlers(bot)
        
        # 3. Configure webhook
        manage_webhook()
        
        logger.info("✅ Bot initialization complete")
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        raise

@app.route(f'/{config.BOT_TOKEN}', methods=['POST'])
def webhook():
    logger.info("Webhook endpoint received an update")
    if request.headers.get('X-Telegram-Bot-Api-Secret-Token') != config.WEBHOOK_SECRET:
        logger.warning("⚠️ Unauthorized webhook access attempt")
        return "Unauthorized", 403

    try:
        update_json = request.stream.read().decode("utf-8")
        logger.info(f"Raw update: {update_json}")
        update = telebot.types.Update.de_json(update_json)
        bot.process_new_updates([update])
        return "ok", 200
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        return "error", 500

# Webhook management
def manage_webhook():
    global webhook_initialized, last_error
    try:
        current = bot.get_webhook_info()
        target = f"{config.WEBHOOK_URL}/{config.BOT_TOKEN}"
        
        if current.url != target:
            bot.remove_webhook()
            bot.set_webhook(
                url=target,
                allowed_updates=["message", "callback_query"],
                secret_token=config.WEBHOOK_SECRET
            )
            logger.info("✅ Webhook configured")
            webhook_initialized = True
    except Exception as e:
        last_error = str(e)
        logger.error(f"❌ Webhook setup failed: {last_error}")
        webhook_initialized = False

# Health endpoints
@app.route('/debug')
def debug():
    try:
        return jsonify({
            "bot_ready": bool(bot.get_me()),
            "webhook_url": bot.get_webhook_info().url,
            "pending_updates": bot.get_webhook_info().pending_update_count,
            "handlers_registered": True
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health_check():
    return jsonify({
        "status": "running",
        "webhook_set": webhook_initialized,
        "last_error": last_error
    })

# Other routes
@app.route('/start', methods=['GET', 'POST'])
def start():
    return "Bot is live ✅"

@app.route('/captcha_webhook', methods=['POST'])
def captcha_webhook():
    if request.headers.get('X-API-KEY') != "papa":
        return jsonify({"error": "Invalid key"}), 403
        
    data = request.get_json()
    if request.remote_addr not in ["76.76.21.21", "::1"]:
        return jsonify({"error": "Invalid source"}), 403

    try:
        user_id = data.get('user_id')
        captcha_result = data.get('result')
        if not user_id or not captcha_result:
            return jsonify({"error": "Missing data"}), 400
            
        success = process_captcha(user_id, captcha_result)
        return jsonify({
            "success": success,
            "message": "Captcha verified" if success else "Verification failed"
        }), 200 if success else 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Initialization
initialize_bot()

if __name__ == '__main__':
    app.run(debug=True)