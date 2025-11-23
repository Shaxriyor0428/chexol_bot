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
