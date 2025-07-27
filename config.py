import os

# === Telegram Bot Token ===
BOT_TOKEN = "8286348410:AAGJLYonXlEekCg71lMjszIZgqOEQUbhm6Q"
# === Channel Usernames to Check Join ===
REQUIRED_CHANNELS = [
    "@combohamsterdailys",
    "@pmdncha"
]

# === Admin Telegram User ID ===
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))

# === CAPTCHA Webhook API Secret or URL ===
CAPTCHA_WEBAPP_URL = "https://catchdogs.vercel.app"
CAPTCHA_API_URL = "https://catchdogs.vercel.app/api/onWebhook"

CAPTCHA_API_KEY = "papa"  # Changed to "papa" as requested
# === Airtime/Data withdrawal notification channel ===
WITHDRAW_CHANNEL = "@combohamsterdailys"

# === Public bot link (for display in withdrawal message) ===
BOT_LINK = "https://t.me/YourBotUsername"

# === Webhook URL for Render or production (used to register webhook) ===
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://your-render-url.onrender.com")

# === Initial balance settings (optional) ===
INITIAL_BALANCE = 0

# === Referral reward (optional) ===
REF_REWARD = 100  # Amount to give on successful referral (optional)

# === Static asset paths ===
FIRE_STICKER_PATH = "static/stickers/fire.webp"
WELCOME_IMAGE_PATH = "templates/welcome.jpg"