import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

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
        "крабстеры",
        "криптон",
        "улётный счёт",
        "спортивные магнаты",
        "wealth & health",
        "vip спецназ",
        "привлекатор",
        "стирая границы",
        "фактор роста",
        "зай, выдавай!",
        "bestsalers",
        "ипотечный шантарам",
        "какие люди!",
        "всё включено",
        "космо продакшн",
        "всё защитано",
        "миллиарды без границ",
        "агрессивный биздев",
        "новый уровень",
        "без потерь",
    ],
    "Процессы": [
        "милый, код довинчен",
        "r.a.i. center",
        "великий комбинатор",
        "бесстрашные pro скуды",
        "скрат",
        "ракета",
        "data stars",
        "кубик рубика",
        "эволюция",
        "на связи",
        "команда э. набиуллиной",
        "the filter",
        "адаптивный горизонт",
        "знахарь kids",
        "совкомпассивити",
        "нейроактивные",
        "кремниевая галина",
        "интроверты",
        "imолодца!",
        "люди важнее",
    ]
}

# Клавиатуры
main_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Продажи", "Процессы")
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
    await message.answer("Выберите категорию:", reply_markup=main_kb)


# Выбор категории
@dp.message_handler(lambda msg: msg.text in ["Продажи", "Процессы"])
async def choose_category(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {"category": message.text}

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for team in categories[message.text]:
        kb.add(team)
    await message.answer("Выберите команду:", reply_markup=kb)


# Выбор команды
@dp.message_handler(lambda msg: True)
async def choose_team(message: types.Message):
    user_id = message.from_user.id
    data = user_data.get(user_id, {})
    category = data.get("category")

    if not category:
        return

    team_name = message.text.strip().lower()
    if team_name not in categories[category]:
        return

    user_data[user_id]["team_name"] = team_name
    await message.answer("Капитан говорит о своей команде?", reply_markup=yes_no_kb)


# Вопросы
@dp.message_handler(lambda msg: msg.text in ["Да", "Нет"])
async def own_team(message: types.Message):
    user_data[message.from_user.id]["is_own_team"] = message.text
    await message.answer("Присутствует новая информация?", reply_markup=yes_no_kb)


@dp.message_handler(lambda msg: msg.text in ["Хорошая", "Средняя", "Слабая", "Не можем оценить"])
async def info_quality(message: types.Message):
    user_data[message.from_user.id]["info_quality"] = message.text
    await message.answer("Является ли методика расчёта результата корректной?", reply_markup=method_validity_kb)


@dp.message_handler(lambda msg: msg.text in ["Некорректно", "Есть ошибки", "Корректная"])
async def method_validity(message: types.Message):
    user_data[message.from_user.id]["method_validity"] = message.text
    await message.answer("Оцените обоснованность предпосылок расчёта", reply_markup=assumptions_kb)


@dp.message_handler(lambda msg: msg.text in ["Оптимистичны", "Реалистичны", "Нереалистичны", "Невозможно оценить"])
async def assumptions_quality(message: types.Message):
    user_data[message.from_user.id]["assumptions_quality"] = message.text
    await message.answer("Верите ли в реалистичность расчёта результата?", reply_markup=result_reliability_kb)


@dp.message_handler(lambda msg: msg.text in ["Верим", "Не верим", "Сомневаемся", "Не можем оценить"])
async def result_reliability(message: types.Message):
    user_data[message.from_user.id]["result_reliability"] = message.text
    await message.answer("Оцените тип оценки экономического результата", reply_markup=result_type_kb)


@dp.message_handler(lambda msg: msg.text in ["Реализован", "Спрогнозирован"])
async def result_type(message: types.Message):
    user_data[message.from_user.id]["result_type"] = message.text
    await message.answer("Какой эффект от проекта?", reply_markup=project_effect_kb)


@dp.message_handler(lambda msg: msg.text in ["Разовый", "Постоянный"])
async def project_effect(message: types.Message):
    user_data[message.from_user.id]["project_effect"] = message.text
    await message.answer("Спасибо 🙏", reply_markup=send_kb)


# Отправка оператору
@dp.message_handler(lambda msg: msg.text == "Отправить данные оператору")
async def send_to_admin(message: types.Message):
    data = user_data.pop(message.from_user.id, {})  # очищаем данные после отправки
    report = (
        f"Команда: {data.get('team_name')}\n"
        f"О своей команде: {data.get('is_own_team')}\n"
        f"Аргументированность: {data.get('info_quality')}\n"
        f"Методика: {data.get('method_validity')}\n"
        f"Предпосылки: {data.get('assumptions_quality')}\n"
        f"Реалистичность: {data.get('result_reliability')}\n"
        f"Тип результата: {data.get('result_type')}\n"
        f"Эффект: {data.get('project_effect')}"
    )
    await bot.send_message(ADMIN_ID, report)
    await message.answer("Данные отправлены оператору ✅", reply_markup=restart_kb)


@dp.message_handler(lambda msg: msg.text == "Оценить другую команду")
async def restart(message: types.Message):
    await message.answer("Выберите категорию:", reply_markup=main_kb)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
