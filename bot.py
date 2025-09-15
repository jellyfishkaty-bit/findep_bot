import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# данные пользователей
user_data = {}

# категории и команды
categories = {
    "Продажи": [
        "Крабстеры", "Криптон", "Улётный счет", "Спортивные Магнаты",
        "Wealth & Health", "VIP спецназ", "Привлекатор", "Стирая границы",
        "Фактор роста", "Зай, выдавай!", "BestSalers", "ИПОТЕЧНЫЙ ШАНТАРАМ",
        "оооо \"Какие Люди!\"", "Все включено", "Космо Продакшн", "Всё ЗАЩИТАно!",
        "Миллиарды. Без границ", "Агрессивный БизДев", "Новый уровень", "\"БЕЗ ПОТЕРЬ\""
    ],
    "Процессы": [
        "Милый, КОД довинчен", "R.A.I. center", "Великий комбинатор", "Бесстрашные Pro СКУДы",
        "Скрат", "Ракета", "Data Stars", "Кубик РубИИка", "Эволюция", "На связИИ",
        "Команда Э. Набиуллиной", "THE FILTER", "Адаптивный горизонт", "Знахарь KIDS",
        "СовкомПассивити", "Нейроактивные + Туса без Джигана", "Кремниевая Галина",
        "Интроверты", "iМолодца!", "#ЛюдиВажнее"
    ]
}

# клавиатуры для вопросов
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


# старт
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    user_data[message.from_user.id] = {}
    kb = InlineKeyboardMarkup()
    for cat in categories.keys():
        kb.add(InlineKeyboardButton(cat, callback_data=f"cat:{cat}"))
    await message.answer("Выберите категорию:", reply_markup=kb)


# выбор категории
@dp.callback_query_handler(lambda c: c.data.startswith("cat:"))
async def choose_category(callback: types.CallbackQuery):
    cat = callback.data.split(":", 1)[1]
    user_data[callback.from_user.id] = {"category": cat}

    kb = InlineKeyboardMarkup()
    for team in categories[cat]:
        kb.add(InlineKeyboardButton(team, callback_data=f"team:{team}"))

    await callback.message.answer("Выберите команду:", reply_markup=kb)
    await callback.answer()


# выбор команды
@dp.callback_query_handler(lambda c: c.data.startswith("team:"))
async def choose_team(callback: types.CallbackQuery):
    team = callback.data.split(":", 1)[1]
    user_data[callback.from_user.id]["team_name"] = team
    await callback.message.answer("Капитан говорит о своей команде?", reply_markup=yes_no_kb)
    await callback.answer()


# дальше обычные вопросы
@dp.message_handler(lambda msg: "is_own_team" not in user_data.get(msg.from_user.id, {}))
async def own_team(message: types.Message):
    if message.text not in ["Да", "Нет"]:
        return
    user_data[message.from_user.id]["is_own_team"] = message.text
    await message.answer("Присутствует новая информация?", reply_markup=yes_no_kb)


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


@dp.message_handler(lambda msg: "info_quality" not in user_data.get(msg.from_user.id, {}))
async def info_quality(message: types.Message):
    if message.text not in ["Хорошая", "Средняя", "Слабая", "Не можем оценить"]:
        return
    user_data[message.from_user.id]["info_quality"] = message.text
    await message.answer("Является ли методика расчёта результата корректной?",
                         reply_markup=method_validity_kb)


@dp.message_handler(lambda msg: "method_validity" not in user_data.get(msg.from_user.id, {}))
async def method_validity(message: types.Message):
    if message.text not in ["Некорректно", "Есть ошибки", "Корректная"]:
        return
    user_data[message.from_user.id]["method_validity"] = message.text
    await message.answer("Оцените обоснованность предпосылок расчёта",
                         reply_markup=assumptions_kb)


@dp.message_handler(lambda msg: "assumptions_quality" not in user_data.get(msg.from_user.id, {}))
async def assumptions_quality(message: types.Message):
    if message.text not in ["Оптимистичны", "Реалистичны", "Нереалистичны", "Невозможно оценить"]:
        return
    user_data[message.from_user.id]["assumptions_quality"] = message.text
    await message.answer("Верите ли в реалистичность расчёта результата?",
                         reply_markup=result_reliability_kb)


@dp.message_handler(lambda msg: "result_reliability" not in user_data.get(msg.from_user.id, {}))
async def result_reliability(message: types.Message):
    if message.text not in ["Верим", "Не верим", "Сомневаемся", "Не можем оценить"]:
        return
    user_data[message.from_user.id]["result_reliability"] = message.text
    await message.answer("Оцените тип оценки экономического результата",
                         reply_markup=result_type_kb)


@dp.message_handler(lambda msg: "result_type" not in user_data.get(msg.from_user.id, {}))
async def result_type(message: types.Message):
    if message.text not in ["Реализован", "Спрогнозирован"]:
        return
    user_data[message.from_user.id]["result_type"] = message.text
    await message.answer("Какой эффект от проекта?",
                         reply_markup=project_effect_kb)


@dp.message_handler(lambda msg: "project_effect" not in user_data.get(msg.from_user.id, {}))
async def project_effect(message: types.Message):
    if message.text not in ["Разовый", "Постоянный"]:
        return
    user_data[message.from_user.id]["project_effect"] = message.text
    await message.answer("Спасибо 🙏", reply_markup=send_kb)


# отправка данных оператору
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

    # очищаем данные
    user_data.pop(message.from_user.id, None)

    restart_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Оценить другую команду")
    await message.answer("Данные отправлены оператору ✅", reply_markup=restart_kb)


# перезапуск цикла
@dp.message_handler(lambda msg: msg.text == "Оценить другую команду")
async def restart(message: types.Message):
    kb = InlineKeyboardMarkup()
    for cat in categories.keys():
        kb.add(InlineKeyboardButton(cat, callback_data=f"cat:{cat}"))
    await message.answer("Выберите категорию:", reply_markup=kb)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
