from database import get_user, increment_balance, update_user

def handle_referral(new_user_id: int, referrer_id: int) -> str:
    if new_user_id == referrer_id:
        return "❌ You can't refer yourself."

    new_user = get_user(new_user_id)
    if new_user.get("referred_by"):
        return "✅ Referral already processed."

    # Mark who referred this user and credit bonus
    new_user["referred_by"] = referrer_id
    new_user["balance"] = new_user.get("balance", 0) + 100
    update_user(new_user_id, referred_by=referrer_id, balance=new_user["balance"])

    # Update referrer’s balance
    increment_balance(referrer_id, 100)

    return "🎉 Referral bonus credited!"