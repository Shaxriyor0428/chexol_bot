from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def user_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            # [KeyboardButton(text="📍 Joylashuv yuborish")],
            [KeyboardButton(text="🎁 Taklif linkini olish")],
        ],
        resize_keyboard=True
    )
