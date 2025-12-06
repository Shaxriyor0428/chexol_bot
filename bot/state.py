from aiogram.fsm.state import StatesGroup, State


class PaymentConfirmation(StatesGroup):
    waiting_for_worker_name = State()
