import telebot
import random
import sqlite3
import re
import time  # Импортируем time для задержек
from telebot import apihelper  # Импортируем apihelper для обработки 429

BOT_TOKEN = '7080454540:AAF3xHmY3jvIYQxD5etkalf3zRsC06MaPd0'
bot = telebot.TeleBot(BOT_TOKEN)

user_states = {}
chat_list = []
DATABASE_FILE = 'baza.db'
chat_settings = {}
AD_MESSAGE = "Администрация данного чата против рекламы других проектов 📛"
REACTIONS = ["👍", "👎", "❤️", "🔥", "🎉", "😊", "🤔", "😂"]

def create_table():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            content TEXT UNIQUE
        )
    ''')
    conn.commit()
    conn.close()
    create_media_table()

def create_media_table():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            file_id TEXT NOT NULL,
            UNIQUE (chat_id, type, file_id)
        )
    ''')
    conn.commit()
    conn.close()

def save_message(message):
    if contains_link(message):
        print("Сообщение содержит ссылку, не сохраняем.")
        return

    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    if message.text:
        try:
            cursor.execute("INSERT INTO messages (type, content) VALUES (?, ?)", ('text', message.text))
            conn.commit()
        except sqlite3.IntegrityError:
            print("Сообщение уже есть в базе данных, не сохраняем.")
            conn.rollback()
    elif message.sticker:
        try:
            cursor.execute("INSERT INTO messages (type, content) VALUES (?, ?)", ('sticker', message.sticker.file_id))
            conn.commit()
        except sqlite3.IntegrityError:
            print("Стикер уже есть в базе данных, не сохраняем.")
            conn.rollback()
    elif message.photo:
        try:
            cursor.execute("INSERT INTO chat_media (chat_id, type, file_id) VALUES (?, ?, ?)",
                           (message.chat.id, 'photo', message.photo[-1].file_id))
            conn.commit()
        except sqlite3.IntegrityError:
            print("Фото уже есть в базе данных, не сохраняем.")
            conn.rollback()
    elif message.animation:
        try:
            cursor.execute("INSERT INTO chat_media (chat_id, type, file_id) VALUES (?, ?, ?)",
                           (message.chat.id, 'animation', message.animation.file_id))
            conn.commit()
        except sqlite3.IntegrityError:
            print("GIF уже есть в базе данных, не сохраняем.")
            conn.rollback()

    conn.close()

def get_random_message():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT type, content FROM messages ORDER BY RANDOM() LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result

def get_random_media(chat_id, media_type):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT file_id FROM chat_media WHERE chat_id = ? AND type = ? ORDER BY RANDOM() LIMIT 1", (chat_id, media_type))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return None

create_table()

def contains_link(message):
    if message and message.text:
        link_pattern = re.compile(r'(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)|(t\.me/\S+)')
        return bool(link_pattern.search(message.text))
    return False

@bot.message_handler(commands=['start'], chat_types=['private'])
def start_private(message):
    inline_keyboard = telebot.types.InlineKeyboardMarkup()
    add_to_chat_button = telebot.types.InlineKeyboardButton(text="✏ Добавить в чат", url="https://t.me/vortox_bot?startgroup=true")
    subscribe_button = telebot.types.InlineKeyboardButton(text="✅ Подписаться на канал", url="https://t.me/+wTYMzFT9ev9iYWMy")
    support_button = telebot.types.InlineKeyboardButton(text="💰 Поддержать проект", url="http://t.me/send?start=IVY5kyjDSlsV")
    settings_button = telebot.types.InlineKeyboardButton(text="⚙ Настройки", callback_data='settings')

    inline_keyboard.add(add_to_chat_button)
    inline_keyboard.add(subscribe_button)
    inline_keyboard.add(support_button)
    inline_keyboard.add(settings_button)

    start_message = "Привет 👋!\n\nМеня зовут Вортокс, я бот для бесед, который на основе ваших сообщений генерирует свои собственные. Также могу удалять рекламу! Следите  за новостями, вскоре появятся новые функции 🎁\n\nДобавь меня в беседу и дай мне права администратора."
    bot.send_message(message.chat.id, start_message, reply_markup=inline_keyboard)

@bot.message_handler(commands=['start'], chat_types=['group', 'supergroup'])
def start_group(message):
    pass

@bot.callback_query_handler(func=lambda call: call.data == 'settings')
def settings_callback(call):
    settings_keyboard = telebot.types.InlineKeyboardMarkup()
    add_chat_to_bot_button = telebot.types.InlineKeyboardButton(text="✏ Добавить чат в бота", callback_data='add_chat')
    delete_chat_button = telebot.types.InlineKeyboardButton(text="🗑 Удалить чат из бота", callback_data='delete_chat_menu')
    chats_button = telebot.types.InlineKeyboardButton(text="🗂 Чаты", callback_data='chats')
    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data='back_to_main')

    settings_keyboard.add(add_chat_to_bot_button)
    settings_keyboard.add(delete_chat_button)
    settings_keyboard.add(chats_button)
    settings_keyboard.add(back_button)

    bot.send_message(call.message.chat.id, "Выберите одну из кнопок ниже:", reply_markup=settings_keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'add_chat')
def add_chat_callback(call):
    add_chat_keyboard = telebot.types.InlineKeyboardMarkup()
    added_button = telebot.types.InlineKeyboardButton(text="Готово ✅", callback_data='added')
    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data='back_to_settings')

    add_chat_keyboard.add(added_button)
    add_chat_keyboard.add(back_button)

    message_step1 = "📝 Шаг 1\n\nУбедитесь, что бот добавлен в группу и у него есть права администратора! Для добавления чата необходимо иметь самому права администратора. Если бот не нашел вас в администраторах, но вы им являетесь, попробуйте убрать в настройках чата анонимность."
    bot.send_message(call.message.chat.id, message_step1, reply_markup=add_chat_keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'added')
def added_callback(call):
    user_id = call.from_user.id
    message_step2 = "📝 Шаг 2\n\nОтправьте ссылку на чат (начинается с t.me/...) или напишите 'private', если это приватный чат, в который вы добавили бота:"
    step2_keyboard = telebot.types.InlineKeyboardMarkup()
    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data='back_to_step1')
    step2_keyboard.add(back_button)

    bot.send_message(call.message.chat.id, message_step2, reply_markup=step2_keyboard)
    user_states[user_id] = 'waitin
