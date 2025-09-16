import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# ==========================
# Список команд
# ==========================
sales_teams = [
    "ReVeRs", "Шикарный гибкий гладиолус", 
]

process_teams = [
    "iМолодца", "Нейроактивные", 
]

# ==========================
# Состояния
# ==========================
class EvalForm(StatesGroup):
    category = State()
    team_name = State()
    is_own_team = State()
    is_new_info = State()
    info_quality = State()
    comment = State()
    finish = State()

# ==========================
# Клавиатуры
# ==========================
category_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Продажи", "Процессы")
yes_no_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Да", "Нет")
info_quality_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    "Хорошая", "Средняя", "Слабая", "Не можем оценить"
)
send_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Отправить данные оператору")
restart_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Перейти к оценке другой команды")

# ==========================
# Хендлеры
# ==========================
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await EvalForm.category.set()
    await message.answer("Привет 👋\nВыбери категорию команды:", reply_markup=category_kb)

# Категория
@dp.message_handler(state=EvalForm.category)
async def choose_category(message: types.Message, state: FSMContext):
    if message.text not in ["Продажи", "Процессы"]:
        return
    await state.update_data(category=message.text)

    # Создаём клавиатуру с командами
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    teams = sales_teams if message.text == "Продажи" else process_teams
    for team in teams:
        kb.add(team)

    await EvalForm.team_name.set()
    await message.answer("Теперь выбери команду:", reply_markup=kb)

# Название команды
@dp.message_handler(state=EvalForm.team_name)
async def get_team(message: types.Message, state: FSMContext):
    await state.update_data(team_name=message.text)
    await EvalForm.is_own_team.set()
    await message.answer("Капитан говорит о своей команде?", reply_markup=yes_no_kb)

# Своя команда или нет
@dp.message_handler(state=EvalForm.is_own_team)
async def own_team(message: types.Message, state: FSMContext):
    if message.text not in ["Да", "Нет"]:
        return
    await state.update_data(is_own_team=message.text)
    await EvalForm.is_new_info.set()
    await message.answer("Присутствует новая информация?", reply_markup=yes_no_kb)

# Новая информация
@dp.message_handler(state=EvalForm.is_new_info)
async def new_info(message: types.Message, state: FSMContext):
    if message.text not in ["Да", "Нет"]:
        return
    await state.update_data(is_new_info=message.text)

    if message.text == "Нет":
        await EvalForm.comment.set()
        await message.answer("Добавь комментарий (по желанию).")
    else:
        await EvalForm.info_quality.set()
        await message.answer("Оцените достоверность и аргументированность информации:",
                             reply_markup=info_quality_kb)

# Достоверность
@dp.message_handler(state=EvalForm.info_quality)
async def info_quality(message: types.Message, state: FSMContext):
    if message.text not in ["Хорошая", "Средняя", "Слабая", "Не можем оценить"]:
        return
    await state.update_data(info_quality=message.text)
    await EvalForm.comment.set()
    await message.answer("Добавь комментарий (по желанию).")

# Комментарий
@dp.message_handler(state=EvalForm.comment)
async def comment(message: types.Message, state: FSMContext):
    await state.update_data(comment=message.text)
    await EvalForm.finish.set()
    await message.answer("Спасибо 🙏", reply_markup=send_kb)

# Отправка данных оператору
@dp.message_handler(lambda msg: msg.text == "Отправить данные оператору", state=EvalForm.finish)
async def send_to_admin(message: types.Message, state: FSMContext):
    data = await state.get_data()
    report = (
        f"Категория: {data.get('category')}\n"
        f"Команда: {data.get('team_name')}\n"
        f"О своей команде: {data.get('is_own_team')}\n"
        f"Новая информация: {data.get('is_new_info')}\n"
        f"Аргументированность: {data.get('info_quality')}\n"
        f"Комментарий: {data.get('comment')}"
    )
    await bot.send_message(ADMIN_ID, report)
    await message.answer("Данные отправлены оператору ✅", reply_markup=restart_kb)
    await state.finish()

# Перезапуск
@dp.message_handler(lambda msg: msg.text == "Перейти к оценке другой команды")
async def restart(message: types.Message):
    await EvalForm.category.set()
    await message.answer("Выбери категорию команды:", reply_markup=category_kb)

# ==========================
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

