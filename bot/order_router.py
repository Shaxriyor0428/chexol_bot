from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from asyncio import sleep
from bot.services.user import update_order, get_user_by_chat
from bot.state import PaymentConfirmation
from bot.services.httpx_client import APIClient
api = APIClient()

router = Router()

@router.callback_query(F.data.startswith("confirm_payment_"))
async def confirm_payment(callback: types.CallbackQuery, state: FSMContext):
    order_id = callback.data.replace("confirm_payment_", "")

    # Tugmalarni o‘chirib qo‘yamiz
    await callback.message.edit_reply_markup()

    # State ichida order_id saqlab qo‘yamiz
    await state.update_data(order_id=order_id)

    # 1️⃣ Hozirgi buyurtma holatini backenddan tekshir
    order = await api.get(f"/orders/{order_id}/")
    if not order or "id" not in order:
        await callback.message.reply("❌ Buyurtma topilmadi.")
        return await state.clear()

    if order["payment_status"] == "paid" and order["processed_by_name"]:
        await callback.message.reply(
            f"❌ Bu buyurtma allaqachon tasdiqlangan 👷 "
            f"({order['processed_by_name']}) tomonidan."
        )
        return await state.clear()

    if order["payment_status"] == "unpaid" and order["processed_by_name"]:
        await callback.message.reply(
            f"❌ Bu buyurtma allaqachon rad qilingan 👷 "
            f"({order['processed_by_name']}) tomonidan."
        )
        return await state.clear()

    await callback.message.answer(
        "👷 Iltimos, to‘lovni tasdiqlagan xodim ismini kiriting:"
    )

    await state.set_state(PaymentConfirmation.waiting_for_worker_name)

    await callback.answer()



@router.message(PaymentConfirmation.waiting_for_worker_name)
async def process_worker_name(message: types.Message, state: FSMContext):
    worker_name = message.text.strip()

    if len(worker_name) < 2:
        return await message.answer("❗ Iltimos, to‘g‘ri ism kiriting.")

    data = await state.get_data()
    order_id = data.get("order_id")

    # 1️⃣ Hozirgi buyurtma holatini backenddan tekshir
    order = await api.get(f"/orders/{order_id}/")

    if not order or "id" not in order:
        await message.answer("❌ Buyurtma topilmadi.")
        return await state.clear()

    if order["payment_status"] == "paid" and order["processed_by_name"]:
        await message.answer(
            f"❌ Bu buyurtma allaqachon tasdiqlangan 👷 "
            f"({order['processed_by_name']}) tomonidan."
        )
        return await state.clear()

    if order["payment_status"] == "unpaid" and order["processed_by_name"]:
        await message.answer(
            f"❌ Bu buyurtma allaqachon rad qilingan 👷 "
            f"({order['processed_by_name']}) tomonidan."
        )
        return await state.clear()

    # PATCH → payment_status="paid", processed_by_name="Xodim ismi"
    updated = await update_order(order_id, "paid", worker_name)

    if not updated or "id" not in updated:
        await message.answer("❌ Buyurtma topilmadi yoki yangilanmadi.")
        return await state.clear()

    order_number = updated.get("order_number", "Noma'lum")

    await message.answer(
        f"✅ <b>To‘lov tasdiqlandi!</b>\n\n"
        f"📦 Buyurtma raqami: <b>{order_number}</b>\n"
        f"👷 Tasdiqlagan xodim: <b>{worker_name}</b>",
        parse_mode="HTML"
    )

    await state.clear()



@router.callback_query(F.data.startswith("reject_payment_"))
async def reject_payment(callback: types.CallbackQuery, state: FSMContext):
    order_id = callback.data.replace("reject_payment_", "")

    user = await get_user_by_chat(callback.from_user.id)
    await callback.message.edit_reply_markup()

    worker_name = user["full_name"] if user else "Noma'lum"
    # 1️⃣ Hozirgi buyurtma holatini backenddan tekshir
    order = await api.get(f"/orders/{order_id}/")
    if not order or "id" not in order:
        await callback.message.reply("❌ Buyurtma topilmadi.")
        return await state.clear()

    if order["payment_status"] == "paid" and order["processed_by_name"]:
        await callback.message.reply(
            f"❌ Bu buyurtma allaqachon tasdiqlangan 👷 "
            f"({order['processed_by_name']}) tomonidan."
        )
        return await state.clear()

    if order["payment_status"] == "unpaid" and order["processed_by_name"]:
        await callback.message.reply(
            f"❌ Bu buyurtma allaqachon rad qilingan 👷 "
            f"({order['processed_by_name']}) tomonidan."
        )
        return await state.clear()
    updated = await update_order(order_id, "unpaid", worker_name)

    if not updated or "id" not in updated:
        return await callback.message.answer("❌ Buyurtma topilmadi yoki yangilanmadi.")

    order_number = updated.get("order_number", "Noma'lum")


    await callback.message.reply(
        f"❌ <b>To‘lov rad etildi!</b>\n\n"
        f"📦 Buyurtma raqami: <b>{order_number}</b>\n"
        f"💳 Holat: <b>Rad etildi</b>\n"
        f"👷 Bekor qilgan xodim: <b>{worker_name}</b>",
        parse_mode="HTML"
    )

    return await callback.answer()





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
