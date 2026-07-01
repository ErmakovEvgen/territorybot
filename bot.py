import asyncio
import logging
import re
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from keyboards import group_buttons, confirm_buttons, edit_field_buttons, schedule_buttons, start_button  
from google_utils import get_worksheet
from datetime import datetime
from dotenv import load_dotenv
import os
import traceback

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
SHEET_ID = "1lB2XOye8C3dU-oXa3Xx7CmbSbr43FQeFkz5QQXVjLvg"

GROUPS = [
    "Танцы 6-10 лет", "Танцы 11-13 лет", "Танцы 14-16 лет",
    "Самбо 4-6 лет", "Самбо 7+ лет", "Брейкинг 6+ лет"
]
REMOVE = types.ReplyKeyboardRemove()
AGE_MIN, AGE_MAX = 4, 17
PHONE_MIN, PHONE_MAX = 11, 11

class TrialStates(StatesGroup):
    waiting_for_group = State()
    waiting_for_time = State()
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_phone = State()
    confirming = State()
    editing_field = State()
    editing_name = State()
    editing_age = State()
    editing_group = State()
    editing_phone = State()
    editing_time = State()

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

def is_valid_age(age_str: str) -> bool:
    return age_str.isdigit() and AGE_MIN <= int(age_str) <= AGE_MAX


_phone_re = re.compile(r'^\+?\d{11}$')
def is_valid_phone(phone_str: str) -> bool:

    return bool(_phone_re.match(phone_str.strip()))

def is_valid_name(name_str: str) -> bool:
    return bool(re.fullmatch(r"[А-Яа-яЁё\s\-]+", name_str.strip()))

def get_confirm_text(data: dict) -> str:
    return (
        "Проверьте корректность введённых данных\n"
        f"Имя: {data.get('name', '')}\n"
        f"Возраст: {data.get('age', '')}\n"
        f"Группа: {data.get('group', '')}\n"
        f"Время: {data.get('time', '')}\n"
        f"Телефон: {data.get('phone', '')}"
    )

async def send_and_set_state(message: Message, text: str, state: FSMContext, new_state: State, reply_markup=None):
    await message.answer(text, reply_markup=reply_markup)
    await state.set_state(new_state)

@dp.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    await message.answer(
        "Добрый день! Чтобы записать ребенка на первое занятие выберите направление:\n"
        "- Танцы 6-10 лет\n- Танцы 11-13 лет\n- Танцы 14-16 лет\n- Самбо 4-6 \n- Самбо 7+ лет\n- Брейкинг 6+ лет",
        reply_markup=group_buttons
    )
    await state.set_state(TrialStates.waiting_for_group)

@dp.message(TrialStates.waiting_for_group)
async def process_group(message: Message, state: FSMContext):
    group = message.text.strip()
    if group not in GROUPS:
        await message.answer("Пожалуйста, выберите направление с помощью кнопок.")
        return
    await state.update_data(group=group)
    schedule = schedule_buttons.get(group)
    if schedule:
        await send_and_set_state(message, "Выберите удобный день и время:", state, TrialStates.waiting_for_time, reply_markup=schedule)
    else:
        await message.answer("В данный момент на данное направление нет расписания.", reply_markup=REMOVE)
        await state.clear()

@dp.message(TrialStates.waiting_for_time)
async def process_time(message: Message, state: FSMContext):
    data = await state.get_data()
    group = data.get("group")
    valid_times = schedule_buttons.get(group)
    if not valid_times:
        await message.answer("В данный момент на данное направление нет расписания.", reply_markup=REMOVE)
        await state.clear()
        return
    valid_texts = [btn.text for row in valid_times.keyboard for btn in row]
    time = message.text.strip()
    if time not in valid_texts:
        await message.answer("Пожалуйста, выберите время с помощью кнопок.")
        return
    await state.update_data(time=time)
    await send_and_set_state(message, "Введите имя и фамилию ребёнка:", state, TrialStates.waiting_for_name, reply_markup=REMOVE)

@dp.message(TrialStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if not is_valid_name(name):
        await message.answer("Пожалуйста, введите имя и фамилию только русскими буквами.")
        return
    await state.update_data(name=name)
    await send_and_set_state(message, "Введите возраст ребёнка:", state, TrialStates.waiting_for_age)

@dp.message(TrialStates.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    age = message.text.strip()
    if not is_valid_age(age):
        await message.answer(f"Пожалуйста, введите корректный возраст (от {AGE_MIN} до {AGE_MAX}).")
        return
    await state.update_data(age=age)
    await send_and_set_state(message, "Укажите Ваш контактный номер телефона:", state, TrialStates.waiting_for_phone)

@dp.message(TrialStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    if not is_valid_phone(phone):
        await message.answer("Пожалуйста, введите корректный номер телефона. Пример: +7912312123 или 89991234567.")
        return
    await state.update_data(phone=phone)
    data = await state.get_data()
    await message.answer(get_confirm_text(data), reply_markup=confirm_buttons)
    await state.set_state(TrialStates.confirming)

@dp.message(TrialStates.confirming)
async def process_confirming(message: Message, state: FSMContext):
    text = message.text.strip()
    if text == "Подтвердить":
        data = await state.get_data()
        if data.get("processing"):
            await message.answer("Запись уже выполняется, пожалуйста дождитесь результата.", reply_markup=REMOVE)
            return
        await state.update_data(processing=True)
        processing_message = await message.answer("Ожидайте...🔄", reply_markup=REMOVE)

        required_fields = ['name', 'age', 'group', 'time', 'phone']
        if not all(data.get(f) for f in required_fields):
            await message.answer("Ошибка: не все данные заполнены. Попробуйте начать заново командой /start.")
            await state.clear()
            return

        try:
            worksheet = get_worksheet(SHEET_ID)
            worksheet.append_row([
                data['name'],
                data['age'],
                data['group'],
                data['time'],
                data['phone'],
                message.from_user.id,
                datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            ])

            group = data['group']
            if group.startswith("Самбо"):
                final_msg = (
                    f"Приглашаем на занятие в:\n"
                    f"🗓️{data['time']}\n"
                    f"Подходить за 10 минут до начала.\n"
                    f"📍Мы находимся по адресу ул. Уральских рабочих, 43, 2 этаж. Вход магазин Стомак/Магнит.\n"
                    f"👟С собой сменная обувь - тапки/сланцы, бутылочка воды.\n"
                    f"👕Одежда: футболка, шорты, носки/чешки. Для девочек - волосы собраны.\n"
                    f"✔️Стоимость первого занятия - 500₽\n\n"
                    f"📞При возникновении вопросов +79292165126\n"
                    f"🌐Наш VK https://vk.com/territory_pobed"
                )
            else:
                final_msg = (
                    f"Приглашаем на занятие в: \n🗓️{data['time']}\n"
                    f"Подходить за 10 минут до начала. \n"
                    f"📍Мы находимся по адресу ул. Уральских рабочих, 43, 2 этаж. Вход магазин Стомак/Магнит.\n"
                    f"👟С собой сменная обувь - кроссовки (желательно на светлой подошве), бутылочка воды. \n"
                    f"👕Одежда: футболка, спортивные штаны. Для девочек - волосы собраны.\n"
                    f"✔️Стоимость первого занятия - 500₽.\n\n"
                    f"📞При возникновении вопросов +79292165126\n"
                    f"🌐Наш VK https://vk.com/territory_pobed"
                )
            await message.answer(final_msg, reply_markup=start_button) 
            try:
                await processing_message.delete()
            except Exception:
                pass

        except Exception as e:
            logger.error("Ошибка при записи в таблицу: %s", e)
            traceback.print_exc()
            await message.answer(f"Ошибка при записи в таблицу: {e}", reply_markup=REMOVE)
            try:
                await processing_message.delete()
            except Exception:
                pass

        await state.clear()

    elif text == "Редактировать":
        await message.answer("Что требуется изменить?", reply_markup=edit_field_buttons)
        await state.set_state(TrialStates.editing_field)
    else:
        await message.answer("Пожалуйста, выберите действие с помощью кнопок.")

@dp.message(TrialStates.editing_field)
async def process_editing_field(message: Message, state: FSMContext):
    mapping = {
        "Имя": (TrialStates.editing_name, "Введите новое имя и фамилию:", REMOVE),
        "Возраст": (TrialStates.editing_age, "Введите новый возраст:", REMOVE),
        "Группа": (TrialStates.editing_group, "Выберите новое направление:", group_buttons),
        "Время": (TrialStates.editing_time, "Выберите новое время:", None),
        "Телефон": (TrialStates.editing_phone, "Введите новый номер телефона:", REMOVE),
    }
    choice = message.text
    if choice == "Вернуться":
        data = await state.get_data()
        await message.answer(get_confirm_text(data), reply_markup=confirm_buttons)
        await state.set_state(TrialStates.confirming)
    elif choice in mapping:
        new_state, prompt, markup = mapping[choice]
        if choice == "Время":
            data = await state.get_data()
            group = data.get("group")
            schedule = schedule_buttons.get(group)
            if schedule:
                await send_and_set_state(message, prompt, state, new_state, reply_markup=schedule)
            else:
                await message.answer("Для выбранной группы нет расписания.", reply_markup=REMOVE)
                await state.set_state(TrialStates.confirming)
        else:
            await send_and_set_state(message, prompt, state, new_state, reply_markup=markup)
    else:
        await message.answer("Пожалуйста, выберите поле для редактирования с помощью кнопок.")

@dp.message(TrialStates.editing_name)
async def process_editing_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if not is_valid_name(name):
        await message.answer("Пожалуйста, введите имя и фамилию только русскими буквами.")
        return
    await state.update_data(name=name)
    data = await state.get_data()
    await message.answer(get_confirm_text(data), reply_markup=confirm_buttons)
    await state.set_state(TrialStates.confirming)

@dp.message(TrialStates.editing_age)
async def process_editing_age(message: Message, state: FSMContext):
    age = message.text.strip()
    if not is_valid_age(age):
        await message.answer(f"Пожалуйста, введите корректный возраст (от {AGE_MIN} до {AGE_MAX}).")
        return
    await state.update_data(age=age)
    data = await state.get_data()
    await message.answer(get_confirm_text(data), reply_markup=confirm_buttons)
    await state.set_state(TrialStates.confirming)

@dp.message(TrialStates.editing_group)
async def process_editing_group(message: Message, state: FSMContext):
    group = message.text.strip()
    if group not in GROUPS:
        await message.answer("Пожалуйста, выберите направление с помощью кнопок.")
        return
    await state.update_data(group=group)
    schedule = schedule_buttons.get(group)
    if schedule:
        await send_and_set_state(message, "Выберите новое время:", state, TrialStates.editing_time, reply_markup=schedule)
    else:
        await message.answer("Для выбранной группы нет расписания.", reply_markup=REMOVE)
        await state.set_state(TrialStates.confirming)

@dp.message(TrialStates.editing_time)
async def process_editing_time(message: Message, state: FSMContext):
    data = await state.get_data()
    group = data.get("group")
    valid_times = schedule_buttons.get(group)
    if not valid_times:
        await message.answer("Для выбранной группы нет расписания.", reply_markup=REMOVE)
        await state.set_state(TrialStates.confirming)
        return
    valid_texts = [btn.text for row in valid_times.keyboard for btn in row]
    time = message.text.strip()
    if time not in valid_texts:
        await message.answer("Пожалуйста, выберите время с помощью кнопок.")
        return
    await state.update_data(time=time)
    data = await state.get_data()
    await message.answer(get_confirm_text(data), reply_markup=confirm_buttons)
    await state.set_state(TrialStates.confirming)

@dp.message(TrialStates.editing_phone)
async def process_editing_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    if not is_valid_phone(phone):
        await message.answer("Пожалуйста, введите корректный номер телефона. Пример: +79991234567 или 89991234567.")
        return
    await state.update_data(phone=phone)
    data = await state.get_data()
    await message.answer(get_confirm_text(data), reply_markup=confirm_buttons)
    await state.set_state(TrialStates.confirming)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
