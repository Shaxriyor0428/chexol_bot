from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from asyncio import sleep

from bot.keyboard import user_menu_keyboard
from bot.services.user import get_user_by_chat, create_user

router = Router()



@router.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    """
    /start yoki /start <ref_id> bilan kirganda ishga tushadi
    """
    args = message.text.split()
    referral_chat_id = None

    # /start <ref_id> bo‘lsa, uni ajratib olamiz
    if len(args) > 1:
        try:
            referral_chat_id = int(args[1])
        except ValueError:
            referral_chat_id = None

    # 🟩 Userni chat_id orqali olish
    user = await get_user_by_chat(message.chat.id)

    # 🟨 Agar user mavjud bo‘lmasa — yaratamiz (referral bilan bo‘lsa qo‘shamiz)
    if not user:
        await create_user(user_chat_id=message.chat.id, referral_chat_id=referral_chat_id)
        user = await get_user_by_chat(message.chat.id)

    # 🟧 Agar foydalanuvchi ro‘yxatdan o‘tmagan bo‘lsa (region yo‘q bo‘lsa)
    print(user)
    if not user or not user["phone"]:
        return await message.answer(
            "👋 Salom!\n\n"
            "Iltimos, avval web ilova orqali ro‘yxatdan o‘ting 👇"
        )

    # 🟦 Aks holda asosiy menyuni ko‘rsatamiz
    return await message.answer(
        "🎯 Asosiy menyu 👇",
        reply_markup=user_menu_keyboard()
    )


@router.message(F.text == "🎁 Taklif linkini olish")
async def invite_link_handler(message: types.Message):
    user = await get_user_by_chat(message.chat.id)
    if not user:
        return await message.answer(
            "❌ <b>Siz ro‘yxatdan o‘tmagansiz.</b>\n\n"
            "Iltimos, avval web ilova orqali ro‘yxatdan o‘ting 👇"
        )

    bot_username = (await message.bot.me()).username
    invite_link = f"https://t.me/{bot_username}?start={user["chat_id"]}"

    text = (
        "🎉 <b>Do‘stlaringizni taklif qiling va har bir buyurtmadan keshbek olasiz!</b>\n\n"
        f"👇 Quyidagi havolani ulashing:\n\n<code>{invite_link}</code>\n\n"
        "📩 Har bir taklif uchun siz buyurtmalardan keshbek to‘playsiz 💎"
    )

    # 🔘 Inline tugma yasaymiz
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📋 Nusxalash uchun bosish",
        switch_inline_query=invite_link,  # Bu foydalanuvchining “inline query”siga kiritadi (copy uchun qulay)
    )

    await message.answer(text, reply_markup=builder.as_markup())



@router.message()
async def message_handler(message: types.Message):
    if message.chat.type != "private":
        return

    warning_msg = await message.answer("⚠️ Noto‘g‘ri ma’lumot kiritildi.")

    await sleep(1)
    try:
        await message.delete()
        await warning_msg.delete()
    except Exception as e:
        print(f"❗ Xabarni o‘chirishda xatolik: {e}")
