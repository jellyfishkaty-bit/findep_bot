import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

# ====== ENV ======
API_TOKEN = os.getenv("API_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# ====== LOGGING ======
logging.basicConfig(level=logging.INFO)

# ====== BOT ======
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


# ====== KEYBOARDS ======
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
after_send_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    "Перейти к оценке другой команды", "Закончить"
)


# ====== STATES ======
class EvalFlow(StatesGroup):
    TeamName = State()
    IsOwnTeam = State()
    IsNewInfo = State()
    InfoQuality = State()
    MethodValidity = State()
    Assumptions = State()
    ResultReliability = State()
    ResultType = State()
    ProjectEffect = State()
    ReadyToSend = State()


# ====== HELPERS ======
async def show_start(message: types.Message):
    await message.answer("Привет 👋 Нажми «Старт», чтобы начать оценку.", reply_markup=start_kb)


def safe(v):
    return v if v else "—"


async def send_report_to_admin(data: dict):
    report = (
        f"Команда: {safe(data.get('team_name'))}\n"
        f"О своей команде: {safe(data.get('is_own_team'))}\n"
        f"Новая информация: {safe(data.get('is_new_info'))}\n"
        f"Аргументированность: {safe(data.get('info_quality'))}\n"
        f"Методика: {safe(data.get('method_validity'))}\n"
        f"Предпосылки: {safe(data.get('assumptions_quality'))}\n"
        f"Реалистичность результата: {safe(data.get('result_reliability'))}\n"
        f"Тип результата: {safe(data.get('result_type'))}\n"
        f"Эффект: {safe(data.get('project_effect'))}"
    )
    await bot.send_message(ADMIN_ID, report)


# ====== UNIVERSAL ENTRY ======
@dp.message_handler(commands=["start", "cancel"])
async def start_cmd(message: types.Message, state: FSMContext):
    await state.finish()
    await show_start(message)


@dp.message_handler(lambda m: m.text == "Старт", state="*")
async def start_flow(message: types.Message, state: FSMContext):
    await state.finish()
    await EvalFlow.TeamName.set()
    await message.answer(
        "Введи название команды, которую хочешь оценить.",
        reply_markup=ReplyKeyboardRemove(),
    )


# Если нет активного состояния — любое сообщение показывает кнопку «Старт»
@dp.message_handler(state="*")
async def fallback_when_idle(message: types.Message, state: FSMContext):
    current = await state.get_state()
    if current is None and message.text != "Старт":
        await show_start(message)


# ====== FLOW ======
@dp.message_handler(state=EvalFlow.TeamName)
async def s_team(message: types.Message, state: FSMContext):
    await state.update_data(team_name=message.text.strip())
    await EvalFlow.IsOwnTeam.set()
    await message.answer("Капитан говорит о своей команде?", reply_markup=yes_no_kb)


@dp.message_handler(lambda m: m.text in ["Да", "Нет"], state=EvalFlow.IsOwnTeam)
async def s_is_own(message: types.Message, state: FSMContext):
    await state.update_data(is_own_team=message.text)
    await EvalFlow.IsNewInfo.set()
    await message.answer("Присутствует новая информация?", reply_markup=yes_no_kb)


@dp.message_handler(lambda m: m.text in ["Да", "Нет"], state=EvalFlow.IsNewInfo)
async def s_new_info(message: types.Message, state: FSMContext):
    await state.update_data(is_new_info=message.text)
    if message.text == "Нет":
        # сразу к отправке
        await EvalFlow.ReadyToSend.set()
        await message.answer("Спасибо 🙏", reply_markup=send_kb)
    else:
        await EvalFlow.InfoQuality.set()
        await message.answer(
            "Оцените достоверность и аргументированность информации",
            reply_markup=info_quality_kb,
        )


@dp.message_handler(lambda m: m.text in ["Хорошая", "Средняя", "Слабая", "Не можем оценить"], state=EvalFlow.InfoQuality)
async def s_info_quality(message: types.Message, state: FSMContext):
    await state.update_data(info_quality=message.text)
    await EvalFlow.MethodValidity.set()
    await message.answer("Является ли методика расчёта результата корректной?",
                         reply_markup=method_validity_kb)


@dp.message_handler(lambda m: m.text in ["Некорректно", "Есть ошибки", "Корректная"], state=EvalFlow.MethodValidity)
async def s_method(message: types.Message, state: FSMContext):
    await state.update_data(method_validity=message.text)
    await EvalFlow.Assumptions.set()
    await message.answer("Оцените обоснованность предпосылок расчёта",
                         reply_markup=assumptions_kb)


@dp.message_handler(lambda m: m.text in ["Оптимистичны", "Реалистичны", "Нереалистичны", "Невозможно оценить"], state=EvalFlow.Assumptions)
async def s_assumptions(message: types.Message, state: FSMContext):
    await state.update_data(assumptions_quality=message.text)
    await EvalFlow.ResultReliability.set()
    await message.answer("Верите ли в реалистичность расчёта результата?",
                         reply_markup=result_reliability_kb)


@dp.message_handler(lambda m: m.text in ["Верим", "Не верим", "Сомневаемся", "Не можем оценить"], state=EvalFlow.ResultReliability)
async def s_reliability(message: types.Message, state: FSMContext):
    await state.update_data(result_reliability=message.text)
    await EvalFlow.ResultType.set()
    await message.answer("Оцените тип оценки экономического результата",
                         reply_markup=result_type_kb)


@dp.message_handler(lambda m: m.text in ["Реализован", "Спрогнозирован"], state=EvalFlow.ResultType)
async def s_result_type(message: types.Message, state: FSMContext):
    await state.update_data(result_type=message.text)
    await EvalFlow.ProjectEffect.set()
    await message.answer("Какой эффект от проекта?", reply_markup=project_effect_kb)


@dp.message_handler(lambda m: m.text in ["Разовый", "Постоянный"], state=EvalFlow.ProjectEffect)
async def s_effect(message: types.Message, state: FSMContext):
    await state.update_data(project_effect=message.text)
    await EvalFlow.ReadyToSend.set()
    await message.answer("Спасибо 🙏", reply_markup=send_kb)


# ====== SEND / AFTER ======
@dp.message_handler(lambda m: m.text == "Отправить данные оператору", state=EvalFlow.ReadyToSend)
async def s_send(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try:
        await send_report_to_admin(data)
        await message.answer("Данные отправлены оператору ✅", reply_markup=after_send_kb)
    except Exception as e:
        await message.answer(f"Не удалось отправить админу: {e}")


@dp.message_handler(lambda m: m.text == "Перейти к оценке другой команды", state="*")
async def s_again(message: types.Message, state: FSMContext):
    await state.finish()
    await EvalFlow.TeamName.set()
    await message.answer("Введи название новой команды, которую хочешь оценить.",
                         reply_markup=ReplyKeyboardRemove())


@dp.message_handler(lambda m: m.text == "Закончить", state="*")
async def s_finish(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Спасибо, работа завершена 🙌", reply_markup=ReplyKeyboardRemove())


# ====== DIAGNOSTICS ======
@dp.message_handler(commands=["ping"], state="*")
async def ping(message: types.Message):
    try:
        await bot.send_message(ADMIN_ID, "Тест: бот может писать админу ✅")
        await message.answer("Пробный сигнал отправлен админу ✅")
    except Exception as e:
        await message.answer(f"Ошибка при отправке админу: {e}")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
