#utils/referral.py
from database import get_user, increment_balance, update_user

def process_referral(new_user_id: int, referrer_id: int) -> str:
    if new_user_id == referrer_id:
        return "❌ You can't refer yourself."

    new_user = get_user(new_user_id)
    if new_user.get("referred_by"):
        return "✅ Referral already processed."

    # Mark who referred this user
    new_user["referred_by"] = referrer_id
    new_user["balance"] += 100
    update_user(new_user_id, referrer_id=referrer_id)

    # Update referrer’s balance
    increment_balance(referrer_id, 100)

    return "🎉 Referral bonus credited!"