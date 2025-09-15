import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Данные пользователей
user_data = {}

# Категории и команды
categories = {
    "Продажи": [
        "Крабстеры", "Криптон", "Улётный счет", "Спортивные Магнаты", "Wealth & Health",
        "VIP спецназ", "Привлекатор", "Стирая границы", "Фактор роста", "Зай, выдавай!",
        "BestSalers", "ИПОТЕЧНЫЙ ШАНТАРАМ", "оооо \"Какие Люди!\"", "Все включено",
        "Космо Продакшн", "Всё ЗАЩИТАно!", "Миллиарды. Без границ",
        "Агрессивный БизДев", "Новый уровень", "\"БЕЗ ПОТЕРЬ\""
    ],
    "Процессы": [
        "Милый, КОД довинчен", "R.A.I. center", "Великий комбинатор", "Бесстрашные Pro СКУДы",
        "Скрат", "Ракета", "Data Stars", "Кубик РубИИка", "Эволюция", "На связИИ",
        "Команда Э. Набиуллиной", "THE FILTER", "Адаптивный горизонт", "Знахарь KIDS",
        "СовкомПассивити", "Нейроактивные + Туса без Джигана", "Кремниевая Галина",
        "Интроверты", "iМолодца!", "#ЛюдиВажнее"
    ]
}

# Клавиатуры
category_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Продажи", "Процессы")
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
restart_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Оценить другую команду")


# Старт
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    user_data[message.from_user.id] = {}
    await message.answer("Привет 👋\nВыберите категорию:", reply_markup=category_kb)


# Категория
@dp.message_handler(lambda msg: msg.text in categories.keys())
async def choose_category(message: types.Message):
    user_data[message.from_user.id] = {"category": message.text}
    teams_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for team in categories[message.text]:
        teams_kb.add(KeyboardButton(team))
    await message.answer("Выберите команду:", reply_markup=teams_kb)


# Команда
@dp.message_handler(lambda msg: any(msg.text in teams for teams in categories.values()))
async def choose_team(message: types.Message):
    user_data[message.from_user.id]["team_name"] = message.text
    await message.answer("Капитан говорит о своей команде?", reply_markup=yes_no_kb)


# Вопрос 1
@dp.message_handler(lambda msg: "is_own_team" not in user_data.get(msg.from_user.id, {}))
async def own_team(message: types.Message):
    if message.text not in ["Да", "Нет"]:
        return
    user_data[message.from_user.id]["is_own_team"] = message.text
    await message.answer("Присутствует новая информация?", reply_markup=yes_no_kb)


# Вопрос 2
@dp.message_handler(lambda msg: "is_new_info" not in user_data.get(msg.from_user.id, {}))
async def new_info(message: types.Message):
    if message.text not in ["Да", "Нет"]:
        return
    user_data[message.from_user.id]["is_new_info"] = message.text
    if message.text == "Нет":
        await message.answer("Спасибо 🙏", reply_markup=send_kb)
    else:
        await message.answer("Оцените достоверность и аргументированность информации",
                             reply_markup=info_quality_kb)


# Вопрос 3
@dp.message_handler(lambda msg: "info_quality" not in user_data.get(msg.from_user.id, {}))
async def info_quality(message: types.Message):
    if message.text not in ["Хорошая", "Средняя", "Слабая", "Не можем оценить"]:
        return
    user_data[message.from_user.id]["info_quality"] = message.text
    await message.answer("Является ли методика расчёта результата корректной?",
                         reply_markup=method_validity_kb)


# Вопрос 4
@dp.message_handler(lambda msg: "method_validity" not in user_data.get(msg.from_user.id, {}))
async def method_validity(message: types.Message):
    if message.text not in ["Некорректно", "Есть ошибки", "Корректная"]:
        return
    user_data[message.from_user.id]["method_validity"] = message.text
    await message.answer("Оцените обоснованность предпосылок расчёта",
                         reply_markup=assumptions_kb)


# Вопрос 5
@dp.message_handler(lambda msg: "assumptions_quality" not in user_data.get(msg.from_user.id, {}))
async def assumptions_quality(message: types.Message):
    if message.text not in ["Оптимистичны", "Реалистичны", "Нереалистичны", "Невозможно оценить"]:
        return
    user_data[message.from_user.id]["assumptions_quality"] = message.text
    await message.answer("Верите ли в реалистичность расчёта результата?",
                         reply_markup=result_reliability_kb)


# Вопрос 6
@dp.message_handler(lambda msg: "result_reliability" not in user_data.get(msg.from_user.id, {}))
async def result_reliability(message: types.Message):
    if message.text not in ["Верим", "Не верим", "Сомневаемся", "Не можем оценить"]:
        return
    user_data[message.from_user.id]["result_reliability"] = message.text
    await message.answer("Оцените тип оценки экономического результата",
                         reply_markup=result_type_kb)


# Вопрос 7
@dp.message_handler(lambda msg: "result_type" not in user_data.get(msg.from_user.id, {}))
async def result_type(message: types.Message):
    if message.text not in ["Реализован", "Спрогнозирован"]:
        return
    user_data[message.from_user.id]["result_type"] = message.text
    await message.answer("Какой эффект от проекта?",
                         reply_markup=project_effect_kb)


# Вопрос 8
@dp.message_handler(lambda msg: "project_effect" not in user_data.get(msg.from_user.id, {}))
async def project_effect(message: types.Message):
    if message.text not in ["Разовый", "Постоянный"]:
        return
    user_data[message.from_user.id]["project_effect"] = message.text
    await message.answer("Спасибо 🙏", reply_markup=send_kb)


# Отправка оператору
@dp.message_handler(lambda msg: msg.text == "Отправить данные оператору")
async def send_to_admin(message: types.Message):
    data = user_data.get(message.from_user.id, {})
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

    # Чистим данные, чтобы новый цикл был чистым
    user_data.pop(message.from_user.id, None)


# Перезапуск
@dp.message_handler(lambda msg: msg.text == "Оценить другую команду")
async def restart(message: types.Message):
    user_data[message.from_user.id] = {}
    await message.answer("Выберите категорию:", reply_markup=category_kb)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
