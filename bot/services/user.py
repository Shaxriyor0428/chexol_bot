from bot.services.httpx_client import APIClient

api = APIClient()


async def get_user_by_chat(chat_id: int):
    user = await api.get(f"/users/user_by_chat/{chat_id}/")
    # ❗ Agar xato bo'lsa, False qaytaramiz

    if isinstance(user, dict) and user.get("error"):
        return None
    return user



async def create_user(user_chat_id: int, referral_chat_id: int = None):
    data = {
        "chat_id": user_chat_id,
        "referal_chat_id": referral_chat_id,
    }
    user = await api.post("/users/create_user_for_bot/", data=data)
    # print("NATIJA: ", user)
    return user


async def update_order(order_id: str, status: str, processed_by_name: str = None):
    data = {
        "payment_status": status,
        "processed_by_name": processed_by_name
    }
    order = await api.patch(f"/orders/{order_id}/", data=data)
    return order


