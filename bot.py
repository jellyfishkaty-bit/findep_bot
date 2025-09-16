class EvalForm(StatesGroup):
    category = State()
    team_name = State()
    is_own_team = State()
    is_new_info = State()
    info_quality = State()
    comment = State()

# Списки команд
sales_teams = [
    "Крабстеры", "Криптон", "Улётный счет", "Спортивные Магнаты", "Wealth & Health",
    "VIP спецназ", "Привлекатор", "Стирая границы", "Фактор роста", "Зай, выдавай!",
    "BestSalers", "ИПОТЕЧНЫЙ ШАНТАРАМ", "оооо 'Какие Люди!'", "Все включено",
    "Космо Продакшн", "Всё ЗАЩИТАно!", "Миллиарды. Без границ", "Агрессивный БизДев",
    "Новый уровень", '"БЕЗ ПОТЕРЬ"'
]

process_teams = [
    "Милый, КОД довинчен", "R.A.I. center", "Великий комбинатор", "Бесстрашные Pro СКУДы",
    "Скрат", "Ракета", "Data Stars", "Кубик РубИИка", "Эволюция", "На связИИ",
    "Команда Э. Набиуллиной", "THE FILTER", "Адаптивный горизонт", "Знахарь KIDS",
    "СовкомПассивити", "Нейроактивные + Туса без Джигана", "Кремниевая Галина", "Интроверты",
    "iМолодца!", "#ЛюдиВажнее"
]

# Клавиатуры
category_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Продажи", "Процессы")
yes_no_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Да", "Нет")
info_quality_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    "Хорошая", "Средняя", "Слабая", "Не можем оценить"
)
send_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Отправить данные оператору")
restart_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Перейти к оценке другой команды")

# Старт
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await EvalForm.category.set()
    await message.answer("Привет 👋\nВыбери категорию:", reply_markup=category_kb)

# Категория
@dp.message_handler(state=EvalForm.category)
async def choose_category(message: types.Message, state: FSMContext):
    if message.text == "Продажи":
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        for team in sales_teams:
            kb.add(team)
        await EvalForm.team_name.set()
        await message.answer("Выбери команду из категории Продажи:", reply_markup=kb)
    elif message.text == "Процессы":
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        for team in process_teams:
            kb.add(team)
        await EvalForm.team_name.set()
        await message.answer("Выбери команду из категории Процессы:", reply_markup=kb)
    else:
        await message.answer("Пожалуйста, выбери категорию из списка.")

# Название команды
@dp.message_handler(state=EvalForm.team_name)
async def get_team_name(message: types.Message, state: FSMContext):
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
    await EvalForm.info_quality.set()
    await message.answer("Оцените достоверность и аргументированность информации",
                         reply_markup=info_quality_kb)

# Достоверность
@dp.message_handler(state=EvalForm.info_quality)
async def info_quality(message: types.Message, state: FSMContext):
    if message.text not in ["Хорошая", "Средняя", "Слабая", "Не можем оценить"]:
        return
    await state.update_data(info_quality=message.text)
    await EvalForm.comment.set()
    await message.answer("Добавьте комментарий (можно в свободной форме):", reply_markup=types.ReplyKeyboardRemove())

# Комментарий
@dp.message_handler(state=EvalForm.comment)
async def add_comment(message: types.Message, state: FSMContext):
    await state.update_data(comment=message.text)
    await message.answer("Спасибо 🙏", reply_markup=send_kb)
    await state.set_state("finish")

# Отправка данных оператору
@dp.message_handler(lambda msg: msg.text == "Отправить данные оператору", state="finish")
async def send_to_admin(message: types.Message, state: FSMContext):
    data = await state.get_data()
    report = (
        f"Команда: {data.get('team_name')}\n"
        f"О своей команде: {data.get('is_own_team')}\n"
        f"Новая информация: {data.get('is_new_info')}\n"
        f"Аргументированность: {data.get('info_quality')}\n"
        f"Комментарий: {data.get('comment')}"
    )
    await bot.send_message(ADMIN_ID, report)
    await message.answer("Данные отправлены оператору ✅", reply_markup=restart_kb)
    await state.finish()

# Начать заново
@dp.message_handler(lambda msg: msg.text == "Перейти к оценке другой команды")
async def restart(message: types.Message):
    await EvalForm.category.set()
    await message.answer("Выбери категорию:", reply_markup=category_kb)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
