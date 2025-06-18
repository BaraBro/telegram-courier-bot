from aiogram.fsm.state import StatesGroup, State

class LocationStates(StatesGroup):
    waiting_period = State()
    waiting_location = State()