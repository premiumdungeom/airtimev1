# database.py

import json
import os

DB_FILE = 'users.json'

def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as f:
            json.dump({}, f)
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=4)

def get_user(user_id):
    db = load_db()
    return db.get(str(user_id))

def get_user_ref_link(user_id):
    """Generate referral link for user"""
    return f"https://t.me/{config.BOT_USERNAME}?start={user_id}"

def create_user(user_id, referrer_id=None):
    db = load_db()
    if str(user_id) not in db:
        db[str(user_id)] = {
            "user_id": user_id,
            "balance": 0,
            "referrer_id": referrer_id,
            "joined": False,
            "blocked": False,
            "number": None
        }
        save_db(db)

def update_user(user_id, **kwargs):
    db = load_db()
    user_id = str(user_id)
    if user_id in db:
        for key, value in kwargs.items():
            db[user_id][key] = value
        save_db(db)

def increment_balance(user_id, amount):
    db = load_db()
    user_id = str(user_id)
    if user_id in db:
        db[user_id]["balance"] += amount
        save_db(db)

def get_all_users():
    db = load_db()
    return list(db.values())

def is_blocked(user_id):
    user = get_user(user_id)
    return user and user.get("blocked", False)

def block_user(user_id):
    update_user(user_id, blocked=True, joined=False)