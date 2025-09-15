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

# Состояния
class EvalForm(StatesGroup):
    category = State()
    team_name = State()
    is_own_team = State()
    is_new_info = State()
    info_quality = State()
    method_validity = State()
    assumptions_quality = State()
    result_reliability = State()
    result_type = State()
    project_effect = State()

# Клавиатуры
yes_no_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Да", "Нет")
info_quality_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    "Хорошая", "Средняя", "Слабая", "Не можем оценить"
)
method_validity_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    "Некорректно", "Есть ошибки", "Корректная"
)
assumptions_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    "Оптимистичны", "Реалистичны", "Нереалистичны", "Невозможно оценить"
)
result_reliability_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    "Верим", "Не верим", "Сомневаемся", "Не можем оценить"
)
result_type_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    "Реализован", "Спрогнозирован"
)
project_effect_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    "Разовый", "Постоянный"
)
send_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Отправить данные оператору")
restart_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Перейти к оценке другой команды")

# Категории
category_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Продажи", "Процессы")

# Списки команд
sales_teams = [
    "Крабстеры", "Криптон", "Улётный счет", "Спортивные Магнаты",
    "Wealth & Health", "VIP спецназ", "Привлекатор", "Стирая границы",
    "Фактор роста", "Зай, выдавай!", "BestSalers", "ИПОТЕЧНЫЙ ШАНТАРАМ",
    "оооо 'Какие Люди!'", "Все включено", "Космо Продакшн", "Всё ЗАЩИТАно!",
    "Миллиарды. Без границ", "Агрессивный БизДев", "Новый уровень", '"БЕЗ ПОТЕРЬ"'
]

process_teams = [
    "Милый, КОД довинчен", "R.A.I. center", "Великий комбинатор", "Бесстрашные Pro СКУДы",
    "Скрат", "Ракета", "Data Stars", "Кубик РубИИка", "Эволюция", "На связИИ",
    "Команда Э. Набиуллиной", "THE FILTER", "Адаптивный горизонт", "Знахарь KIDS",
    "СовкомПассивити", "Нейроактивные + Туса без Джигана", "Кремниевая Галина",
    "Интроверты", "iМолодца!", "#ЛюдиВажнее"
]

def build_team_keyboard(category: str):
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if category == "Продажи":
        for t in sales_teams:
            kb.add(t)
    else:
        for t in process_teams:
            kb.add(t)
    return kb

# Старт
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
    await EvalForm.team_name.set()
    await message.answer("Выбери команду:", reply_markup=build_team_keyboard(message.text))

# Название команды
@dp.message_handler(state=EvalForm.team_name)
async def get_team_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    category = data.get("category")
    if category == "Продажи" and message.text not in sales_teams:
        return
    if category == "Процессы" and message.text not in process_teams:
        return

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
        await message.answer("Спасибо 🙏", reply_markup=send_kb)
        await state.set_state("finish")  # ждём отправку
    else:
        await EvalForm.info_quality.set()
        await message.answer("Оцените достоверность и аргументированность информации",
                             reply_markup=info_quality_kb)

# Достоверность
@dp.message_handler(state=EvalForm.info_quality)
async def info_quality(message: types.Message, state: FSMContext):
    if message.text not in ["Хорошая", "Средняя", "Слабая", "Не можем оценить"]:
        return
    await state.update_data(info_quality=message.text)
    await EvalForm.method_validity.set()
    await message.answer("Является ли методика расчёта результата корректной?",
                         reply_markup=method_validity_kb)

# Методика
@dp.message_handler(state=EvalForm.method_validity)
async def method_validity(message: types.Message, state: FSMContext):
    if message.text not in ["Некорректно", "Есть ошибки", "Корректная"]:
        return
    await state.update_data(method_validity=message.text)
    await EvalForm.assumptions_quality.set()
    await message.answer("Оцените обоснованность предпосылок расчёта",
                         reply_markup=assumptions_kb)

# Предпосылки
@dp.message_handler(state=EvalForm.assumptions_quality)
async def assumptions_quality(message: types.Message, state: FSMContext):
    if message.text not in ["Оптимистичны", "Реалистичны", "Нереалистичны", "Невозможно оценить"]:
        return
    await state.update_data(assumptions_quality=message.text)
    await EvalForm.result_reliability.set()
    await message.answer("Верите ли в реалистичность расчёта результата?",
                         reply_markup=result_reliability_kb)

# Реалистичность результата
@dp.message_handler(state=EvalForm.result_reliability)
async def result_reliability(message: types.Message, state: FSMContext):
    if message.text not in ["Верим", "Не верим", "Сомневаемся", "Не можем оценить"]:
        return
    await state.update_data(result_reliability=message.text)
    await EvalForm.result_type.set()
    await message.answer("Оцените тип оценки экономического результата",
                         reply_markup=result_type_kb)

# Тип результата
@dp.message_handler(state=EvalForm.result_type)
async def result_type(message: types.Message, state: FSMContext):
    if message.text not in ["Реализован", "Спрогнозирован"]:
        return
    await state.update_data(result_type=message.text)
    await EvalForm.project_effect.set()
    await message.answer("Какой эффект от проекта?",
                         reply_markup=project_effect_kb)

# Эффект проекта
@dp.message_handler(state=EvalForm.project_effect)
async def project_effect(message: types.Message, state: FSMContext):
    if message.text not in ["Разовый", "Постоянный"]:
        return
    await state.update_data(project_effect=message.text)
    await message.answer("Спасибо 🙏", reply_markup=send_kb)
    await state.set_state("finish")

# Отправка данных оператору
@dp.message_handler(lambda msg: msg.text == "Отправить данные оператору", state="finish")
async def send_to_admin(message: types.Message, state: FSMContext):
    data = await state.get_data()
    report = (
        f"Категория: {data.get('category')}\n"
        f"Команда: {data.get('team_name')}\n"
        f"О своей команде: {data.get('is_own_team')}\n"
        f"Новая информация: {data.get('is_new_info')}\n"
        f"Аргументированность: {data.get('info_quality')}\n"
        f"Методика: {data.get('method_validity')}\n"
        f"Предпосылки: {data.get('assumptions_quality')}\n"
        f"Реалистичность результата: {data.get('result_reliability')}\n"
        f"Тип результата: {data.get('result_type')}\n"
        f"Эффект: {data.get('project_effect')}"
    )
    await bot.send_message(ADMIN_ID, report)
    await message.answer("Данные отправлены оператору ✅", reply_markup=restart_kb)
    await state.finish()

# Начать заново
@dp.message_handler(lambda msg: msg.text == "Перейти к оценке другой команды")
async def restart(message: types.Message):
    await EvalForm.category.set()
    await message.answer("Выбери категорию команды:", reply_markup=category_kb)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
