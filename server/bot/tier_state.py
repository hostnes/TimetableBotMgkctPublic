from aiogram.dispatcher.filters.state import State, StatesGroup


class InstallGroupState(StatesGroup):
    get_group = State()


class SendMessage(StatesGroup):
    get_message = State()