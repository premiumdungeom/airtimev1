#utils/referral.py
from database import get_user, update_user_balance, save_referral

def process_referral(new_user_id: int, referrer_id: int) -> str:
    if new_user_id == referrer_id:
        return "❌ You can't refer yourself."

    new_user = get_user(new_user_id)
    if new_user.get("referred_by"):
        return "✅ Referral already processed."

    # Mark who referred this user
    new_user["referred_by"] = referrer_id
    new_user["balance"] += 100  # Optional: Bonus for new user too?
    save_referral(new_user_id, referrer_id)

    # Update referrer’s balance
    referrer = get_user(referrer_id)
    referrer["balance"] += 100
    update_user_balance(referrer_id, referrer["balance"])

    return "🎉 Referral bonus credited!"
