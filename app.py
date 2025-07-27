from flask import Flask, request, jsonify
import telebot
import config
import logging
from keepalive import start_background_tasks, ADMIN_ID, DB_PATH  # Added imports
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
logging.basicConfig(level=logging.INFO)

# Global variables
webhook_initialized = False
last_error = None

app = Flask(__name__)
bot = telebot.TeleBot(config.BOT_TOKEN)

try:
    bot_info = bot.get_me()
    logger.info(f"Bot authorized as @{bot_info.username}")
except Exception as e:
    logger.error(f"Bot auth failed: {e}")
    raise  # Crash early if token invalid

@app.route('/init')
def initialize_app():
    global webhook_initialized
    try:
        start_background_tasks()
        setup_start_handlers(bot)
        manage_webhook()
        return jsonify({"status": "initialized"})
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        return jsonify({"error": str(e)}), 500

# === Webhook route for Telegram messages ===
@app.route('/start', methods=['GET', 'POST'])
def start():
    return "Bot is live ✅"

# === Webhook Security ===
@app.route(f'/{config.BOT_TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('X-Telegram-Bot-Api-Secret-Token') != config.WEBHOOK_SECRET:
        logger.warning("⚠️ Unauthorized webhook access attempt")
        return "Unauthorized", 403
    
    try:
        update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
        bot.process_new_updates([update])
        return "ok", 200
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        return "error", 500

# === CAPTCHA webhook route ===
@app.route('/captcha_webhook', methods=['POST'])
def captcha_webhook():
    # Verify API key
    if request.headers.get('X-API-KEY') != "papa":  # Hardcoded as requested
        return jsonify({"error": "Invalid key"}), 403
        
    data = request.get_json()
    
    # Verify source IP (Vercel IPs)
    if request.remote_addr not in ["76.76.21.21", "::1"]:
        return jsonify({"error": "Invalid source"}), 403

    # Process captcha result
    try:
        user_id = data.get('user_id')
        captcha_result = data.get('result')
        
        if not user_id or not captcha_result:
            return jsonify({"error": "Missing required data"}), 400
            
        # Process the captcha result (implement your logic here)
        success = process_captcha(user_id, captcha_result)
        
        if success:
            return jsonify({"success": True, "message": "Captcha verified"})
        else:
            return jsonify({"success": False, "error": "Captcha verification failed"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# === Single Webhook Manager ===
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

# Initial setup
manage_webhook()

@app.route('/debug')
def debug():
    try:
        return jsonify({
            "bot_ready": bool(bot.get_me()),
            "webhook_url": bot.get_webhook_info().url,
            "pending_updates": bot.get_webhook_info().pending_update_count
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

# === Telegram message handler ===
@bot.message_handler(commands=['start'])
def command_start(message):
    user_id = message.from_user.id
    if is_blocked(user_id):
        bot.send_message(user_id, "🚫 Access Denied: You are not allowed to use this bot.")
        return

    referrer_id = None
    if " " in message.text:
        ref_part = message.text.split(" ", 1)[1]
        if ref_part.isdigit():
            referrer_id = int(ref_part)

    create_user(user_id, referrer_id=referrer_id)
    handle_start(bot, message)

@bot.message_handler(content_types=['document'])
def handle_db_restore(message):
    if str(message.from_user.id) == ADMIN_ID and message.document.file_name == "users.json":
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded = bot.download_file(file_info.file_path)
            with open(DB_PATH, 'wb') as f:
                f.write(downloaded)
            bot.reply_to(message, "✅ Database restored successfully!")
        except Exception as e:
            bot.reply_to(message, f"❌ Restore failed: {str(e)}")

@bot.message_handler(func=lambda m: m.text == "👏 Main Menu")
def menu_handler(message):
    if is_blocked(message.from_user.id):
        return
    handle_mainmenu(bot, message)

@bot.message_handler(func=lambda m: m.text == "👏 Dashboard")
def dash_handler(message):
    if is_blocked(message.from_user.id):
        return
    handle_dashboard(bot, message)

@bot.message_handler(func=lambda m: m.text == "✅ Set Number")
def set_number_prompt(message):
    if is_blocked(message.from_user.id):
        return
    handle_set_number(bot, message)

@bot.message_handler(func=lambda m: m.text and m.text.isdigit() and len(m.text) == 11)
def set_number_process(message):
    if is_blocked(message.from_user.id):
        return
    handle_set_number(bot, message)

@bot.message_handler(func=lambda m: m.text == "💵 Claim as Airtime" or m.text == "💽 Claim as Data")
def claim_handler(message):
    if is_blocked(message.from_user.id):
        return
    handle_claim(bot, message)  # Pass the bot instance

if __name__ == '__main__':
    # Manual initialization when running locally
    start_background_tasks()
    setup_start_handlers(bot)
    manage_webhook()
    app.run(debug=True)