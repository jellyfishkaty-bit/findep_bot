import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup

# Настройки: токен и ID берём из переменных окружения
API_TOKEN = os.getenv("API_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# Логирование
logging.basicConfig(level=logging.INFO)

# Бот и диспетчер
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Словарь для хранения данных пользователя
user_data = {}

# Клавиатуры
start_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Старт")
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


# Первый контакт
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Привет 👋 Нажми кнопку «Старт», чтобы начать оценку.", reply_markup=start_kb)


# Нажатие кнопки Старт
@dp.message_handler(lambda msg: msg.text == "Старт")
async def pressed_start(message: types.Message):
    user_data[message.from_user.id] = {}
    await message.answer("Введи название команды, которую хочешь оценить.", reply_markup=types.ReplyKeyboardRemove())


# Название команды
@dp.message_handler(lambda msg: "team_name" not in user_data.get(msg.from_user.id, {}))
async def get_team_name(message: types.Message):
    user_data[message.from_user.id]["team_name"] = message.text
    await message.answer("Капитан говорит о своей команде?", reply_markup=yes_no_kb)


# Своя/чужая команда
@dp.message_handler(lambda msg: "is_own_team" not in user_data.get(msg.from_user.id, {}))
async def own_team(message: types.Message):
    if message.text not in ["Да", "Нет"]:
        return
    user_data[message.from_user.id]["is_own_team"] = message.text
    await message.answer("Присутствует новая информация?", reply_markup=yes_no_kb)


# Новая информация
@dp.message_handler(lambda msg: "is_new_info" not in user_data.get(msg.from_user.id, {}))
async def new_info(message: types.Message):
    if message.text not in ["Да", "Нет"]:
        return
    user_data[message.from_user.id]["is_new_info"] = message.text
    if message.text == "Нет":
        await message.answer("Спасибо 🙏", reply_markup=send_kb)
    else:
        await message.answer(
            "Оцените достоверность и аргументированность информации",
            reply_markup=info_quality_kb,
        )


# Аргументированность
@dp.message_handler(lambda msg: "info_quality" not in user_data.get(msg.from_user.id, {}))
async def info_quality(message: types.Message):
    if message.text not in ["Хорошая", "Средняя", "Слабая", "Не можем оценить"]:
        return
    user_data[message.from_user.id]["info_quality"] = message.text
    await message.answer("Является ли методика расчёта результата корректной?",
                         reply_markup=method_validity_kb)


# Методика расчёта
@dp.message_handler(lambda msg: "method_validity" not in user_data.get(msg.from_user.id, {}))
async def method_validity(message: types.Message):
    if message.text not in ["Некорректно", "Есть ошибки", "Корректная"]:
        return
    user_data[message.from_user.id]["method_validity"] = message.text
    await message.answer("Оцените обоснованность предпосылок расчёта",
                         reply_markup=assumptions_kb)


# Предпосылки
@dp.message_handler(lambda msg: "assumptions_quality" not in user_data.get(msg.from_user.id, {}))
async def assumptions_quality(message: types.Message):
    if message.text not in ["Оптимистичны", "Реалистичны", "Нереалистичны", "Невозможно оценить"]:
        return
    user_data[message.from_user.id]["assumptions_quality"] = message.text
    await message.answer("Верите ли в реалистичность расчёта результата?",
                         reply_markup=result_reliability_kb)


# Реалистичность
@dp.message_handler(lambda msg: "result_reliability" not in user_data.get(msg.from_user.id, {}))
async def result_reliability(message: types.Message):
    if message.text not in ["Верим", "Не верим", "Сомневаемся", "Не можем оценить"]:
        return
    user_data[message.from_user.id]["result_reliability"] = message.text
    await message.answer("Оцените тип оценки экономического результата",
                         reply_markup=result_type_kb)


# Тип результата
@dp.message_handler(lambda msg: "result_type" not in user_data.get(msg.from_user.id, {}))
async def result_type(message: types.Message):
    if message.text not in ["Реализован", "Спрогнозирован"]:
        return
    user_data[message.from_user.id]["result_type"] = message.text
    await message.answer("Какой эффект от проекта?", reply_markup=project_effect_kb)


# Эффект
@dp.message_handler(lambda msg: "project_effect" not in user_data.get(msg.from_user.id, {}))
async def project_effect(message: types.Message):
    if message.text not in ["Разовый", "Постоянный"]:
        return
    user_data[message.from_user.id]["project_effect"] = message.text
    await message.answer("Спасибо 🙏", reply_markup=send_kb)


# Отправка данных админу
@dp.message_handler(lambda msg: msg.text == "Отправить данные оператору")
async def send_to_admin(message: types.Message):
    data = user_data.get(message.from_user.id, {})
    report = (
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
    try:
        await bot.send_message(ADMIN_ID, report)
        await message.answer("Данные отправлены оператору ✅", reply_markup=types.ReplyKeyboardRemove())
    except Exception as e:
        await message.answer(f"Не удалось отправить админу: {e}")


# Тестовая команда
@dp.message_handler(commands=["ping"])
async def ping(message: types.Message):
    try:
        await bot.send_message(ADMIN_ID, "Тест: бот может писать админу ✅")
        await message.answer("Пробный сигнал отправлен админу ✅")
    except Exception as e:
        await message.answer(f"Ошибка при отправке админу: {e}")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
