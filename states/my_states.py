from aiogram.fsm.state import StatesGroup, State


class FSMFillForm(StatesGroup):
    fill_post_content = State()        # Состояние ожидания ввода содержания поста
    fill_post_sheduled_at = State()    # Состояние ожидания ввода времени публикации поста


class FSMAddCut(StatesGroup):
    select_cat_name = State()
    select_cat_for_subcat = State()
    select_subcat_name = State()