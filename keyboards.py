from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

group_buttons = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Танцы 6-10 лет")],
              [KeyboardButton(text="Танцы 11-13 лет")],
              [KeyboardButton(text="Танцы 14-16 лет")],
              [KeyboardButton(text="Самбо 4-6 лет")],
              [KeyboardButton(text="Самбо 7+ лет")],
              [KeyboardButton(text="Брейкинг 6+ лет")]],
    resize_keyboard=True
)

confirm_buttons = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Редактировать"), KeyboardButton(text="Подтвердить")]],
    resize_keyboard=True
)

edit_field_buttons = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Имя"), KeyboardButton(text="Возраст")],
        [KeyboardButton(text="Группа"), KeyboardButton(text="Телефон")],
        [KeyboardButton(text="Вернуться")]
    ],
    resize_keyboard=True
)

schedule_buttons = {
    "Танцы 6-10 лет": ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Понедельник 19:00")],
                    [KeyboardButton(text="Среда 19:00")],
                    [KeyboardButton(text="Суббота 10:30")]],
        resize_keyboard=True
    ),
    "Танцы 11-13 лет": ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Понедельник 19:30")],
                    [KeyboardButton(text="Четверг 19:30")],
                    [KeyboardButton(text="Суббота 11:30")]],
        resize_keyboard=True
    ),
    "Танцы 14-16 лет": ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Среда 19:30")],
                    [KeyboardButton(text="Четверг 18:30")],
                    [KeyboardButton(text="Суббота 12:30")]],
        resize_keyboard=True
    ),
    "Самбо 4-6 лет": ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Вторник 19:00")],
                    [KeyboardButton(text="Четверг 19:00")]],
        resize_keyboard=True
    ),
    "Самбо 7+ лет": ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Понедельник 18:30")],
                    [KeyboardButton(text="Среда 18:30")],
                    [KeyboardButton(text="Четверг 18:30")]],
        resize_keyboard=True
    ),
    "Брейкинг 6+ лет": ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Вторник 19:00")],
                    [KeyboardButton(text="Пятница 19:00")],
                    [KeyboardButton(text="Суббота 15:00")]],
        resize_keyboard=True
    ),
}

start_button = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="/start")]], 
    resize_keyboard=True
)

