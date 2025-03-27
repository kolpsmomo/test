import telebot
import random
import sqlite3
import re

BOT_TOKEN = '7080454540:AAF3xHmY3jvIYQxD5etkalf3zRsC06MaPd0' # токен сюда
bot = telebot.TeleBot(BOT_TOKEN)

user_states = {}
chat_list = []
DATABASE_FILE = 'baza.db' # имя файла с бд, самому файл с бд не создавать!!! 

chat_settings = {}

AD_MESSAGE = "Администрация данного чата против рекламы других проектов 📛" # сообщение для анти рекл

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

@bot.message_handler(commands=['start'])
def start(message):
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
    message_step2 = "📝 Шаг 2\n\nОтправьте ID чата (начинается с минуса, например -123456789):"
    step2_keyboard = telebot.types.InlineKeyboardMarkup()
    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data='back_to_step1')
    step2_keyboard.add(back_button)

    bot.send_message(call.message.chat.id, message_step2, reply_markup=step2_keyboard)
    user_states[user_id] = 'waiting_for_chat_id'

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == 'waiting_for_chat_id')
def handle_chat_id(message):
    user_id = message.from_user.id
    try:
        chat_id = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, отправьте корректный ID чата (целое число, начинающееся с минуса).")
        return

    if chat_id >= 0:
        bot.send_message(message.chat.id, "ID чата должен быть отрицательным (начинаться с минуса).")
        return

    try:
        if any(chat['id'] == chat_id for chat in chat_list):
            already_added_keyboard = telebot.types.InlineKeyboardMarkup()
            back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data='back_to_settings')
            already_added_keyboard.add(back_button)
            bot.send_message(message.chat.id, "Вы уже добавляли этот чат!", reply_markup=already_added_keyboard)
            if user_id in user_states:
                del user_states[user_states]
            return

        chat_member = bot.get_chat_member(chat_id, bot.get_me().id)
        if chat_member.status not in ['administrator', 'creator']:
            bot.send_message(message.chat.id, "У бота нет прав администратора в этом чате!")
            return

        user_chat_member = bot.get_chat_member(chat_id, user_id)
        if user_chat_member.status not in ['administrator', 'creator']:
            not_admin_keyboard = telebot.types.InlineKeyboardMarkup()
            back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data='back_to_settings')
            not_admin_keyboard.add(back_button)
            bot.send_message(message.chat.id, "Вы не являетесь администратором чата. Если это так, попробуйте убрать анонимность в настройках чата.", reply_markup=not_admin_keyboard)
            if user_id in user_states:
                del user_states[user_states]
            return

        chat_info = bot.get_chat(chat_id)
        chat_name = chat_info.title

        chat_list.append({"id": chat_id, "name": chat_name})

    except telebot.apihelper.ApiTelegramException as e:
        bot.send_message(message.chat.id, f"Не удалось получить имя чата: {e}")
        return

    success_keyboard = telebot.types.InlineKeyboardMarkup()
    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data='back_to_settings')
    success_keyboard.add(back_button)
    bot.send_message(message.chat.id, "Отлично, ваша группа добавлена в список чатов ✅", reply_markup=success_keyboard)

    if user_id in user_states:
        del user_states[user_states]

@bot.callback_query_handler(func=lambda call: call.data == 'back_to_step1')
def back_to_step1_callback(call):
    user_id = call.from_user.id
    add_chat_keyboard = telebot.types.InlineKeyboardMarkup()
    added_button = telebot.types.InlineKeyboardButton(text="Готово ✅", callback_data='added')
    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data='back_to_settings')

    add_chat_keyboard.add(added_button)
    add_chat_keyboard.add(back_button)

    message_step1 = "📝 Шаг 1\n\nУбедитесь, что бот добавлен в группу и у него есть права администратора! Для добавления чата необходимо иметь самому права администратора. Если бот не нашел вас в администраторах, но вы им являетесь, попробуйте убрать в настройках чата анонимность."
    bot.send_message(call.message.chat.id, message_step1, reply_markup=add_chat_keyboard)
    if user_id in user_states:
        del user_states[user_states]

@bot.callback_query_handler(func=lambda call: call.data == 'back_to_main')
def back_to_main_callback(call):
    start(call.message)

@bot.callback_query_handler(func=lambda call: call.data == 'back_to_settings')
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

@bot.callback_query_handler(func=lambda call: call.data == 'delete_chat_menu')
def delete_chat_menu_callback(call):
    if not chat_list:
        no_chats_keyboard = telebot.types.InlineKeyboardMarkup()
        back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data='back_to_settings')
        no_chats_keyboard.add(back_button)
        bot.send_message(call.message.chat.id, "Список чатов пуст. Нечего удалять.", reply_markup=no_chats_keyboard)
        return

    delete_chat_keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    for chat in chat_list:
        delete_button = telebot.types.InlineKeyboardButton(text=chat["name"], callback_data=f"confirm_delete_{chat['id']}")
        delete_chat_keyboard.add(delete_button)

    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data='back_to_settings')
    delete_chat_keyboard.add(back_button)

    bot.send_message(call.message.chat.id, "Выберите чат, который хотите удалить из бота:", reply_markup=delete_chat_keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_delete_'))
def confirm_delete_callback(call):
    chat_id = call.data[15:]

    chat_name = ""
    for chat in chat_list:
        if str(chat['id']) == chat_id:
            chat_name = chat['name']
            break

    confirm_keyboard = telebot.types.InlineKeyboardMarkup()
    yes_button = telebot.types.InlineKeyboardButton(text="Да ✅", callback_data=f"delete_{chat_id}")
    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data='delete_chat_menu')
    confirm_keyboard.add(yes_button)
    confirm_keyboard.add(back_button)

    bot.send_message(call.message.chat.id, f"Вы точно хотите удалить чат \"{chat_name}\"?", reply_markup=confirm_keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_'))
def delete_callback(call):
    chat_id = call.data[7:]

    chat_name = ""
    for chat in chat_list:
        if str(chat['id']) == chat_id:
            chat_name = chat['name']
            break

    chat_list[:] = [chat for chat in chat_list if str(chat['id']) != chat_id]

    success_keyboard = telebot.types.InlineKeyboardMarkup()
    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data='back_to_settings')
    success_keyboard.add(back_button)
    bot.send_message(call.message.chat.id, f"Чат \"{chat_name}\" успешно удален ✅", reply_markup=success_keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'chats')
def chats_callback(call):
    chats_keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)

    if not chat_list:
        empty_keyboard = telebot.types.InlineKeyboardMarkup()
        back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data='back_to_settings')
        empty_keyboard.add(back_button)
        bot.send_message(call.message.chat.id, "Список чатов пуст.", reply_markup=empty_keyboard)

        return

    for chat in chat_list:
        chat_button = telebot.types.InlineKeyboardButton(text=chat["name"], callback_data=f"chat_{chat['id']}")
        chats_keyboard.add(chat_button)

    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data='back_to_settings')
    chats_keyboard.add(back_button)

    bot.send_message(call.message.chat.id, "Выберите чат:", reply_markup=chats_keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('chat_'))
def chat_button_callback(call):
    chat_id = call.data[5:]
    user_id = call.from_user.id

    selected_chat = next((chat for chat in chat_list if str(chat['id']) == chat_id), None)
    if selected_chat:
        chat_name = selected_chat["name"]
        user_states[user_id] = {'chat_id': chat_id, 'chat_name': chat_name}
    else:
        chat_name = "Неизвестный чат" # если баг

    chat_keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    activity_button = telebot.types.InlineKeyboardButton(text="📊 Активность бота", callback_data=f"activity_{chat_id}")
    ads_button = telebot.types.InlineKeyboardButton(text="📛 Реклама в чате", callback_data=f"ads_{chat_id}")
    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data='back_to_chatlist')

    chat_keyboard.add(activity_button)
    chat_keyboard.add(ads_button)
    chat_keyboard.add(back_button)

    bot.send_message(call.message.chat.id, f"Вы выбрали чат \"{chat_name}\" 📣\n\nВыберите одну из кнопок ниже:",
                    reply_markup=chat_keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('activity_'))
def activity_callback(call):
    chat_id = call.data[9:]
    user_id = call.from_user.id

    if user_id in user_states:
        chat_name = user_states[user_id].get('chat_name', "Неизвестный чат")
    else:
        chat_name = "Неизвестный чат" # аналогично

    activity_message = "1 - 20 % активность\n" \
                       "2 - 40 % активность\n" \
                       "3 - 60 % активность\n" \
                       "4 - 80 % активность\n" \
                       "5 - 100 % активность\n\n" \
                       "Выберите активность бота в вашем чате:"

    activity_keyboard = telebot.types.InlineKeyboardMarkup(row_width=5)
    btn1 = telebot.types.InlineKeyboardButton(text="1", callback_data=f"set_activity_{chat_id}_20")
    btn2 = telebot.types.InlineKeyboardButton(text="2", callback_data=f"set_activity_{chat_id}_40")
    btn3 = telebot.types.InlineKeyboardButton(text="3", callback_data=f"set_activity_{chat_id}_60")
    btn4 = telebot.types.InlineKeyboardButton(text="4", callback_data=f"set_activity_{chat_id}_80")
    btn5 = telebot.types.InlineKeyboardButton(text="5", callback_data=f"set_activity_{chat_id}_100")
    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data=f"back_to_chat_{chat_id}")

    activity_keyboard.add(btn1, btn2, btn3, btn4, btn5)
    activity_keyboard.add(back_button)

    bot.send_message(call.message.chat.id, activity_message, reply_markup=activity_keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('ads_'))
def ads_callback(call):
    chat_id = call.data[4:]
    user_id = call.from_user.id

    if user_id in user_states:
        chat_name = user_states[user_id].get('chat_name', "Неизвестный чат")
    else:
        chat_name = "Неизвестный чат" # аналогично

    ads_message = "Если включить эту функцию, то бот будет удалять все сообщения с ссылками 📛.\n\nВыберите одну из кнопок ниже:"

    ads_keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    enable_button = telebot.types.InlineKeyboardButton(text="Включить ✅", callback_data=f"enable_ads_{chat_id}")
    disable_button = telebot.types.InlineKeyboardButton(text="Выключить ⛔", callback_data=f"disable_ads_{chat_id}")
    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data=f"back_to_chat_{chat_id}")

    ads_keyboard.add(enable_button)
    ads_keyboard.add(disable_button)
    ads_keyboard.add(back_button)

    bot.send_message(call.message.chat.id, ads_message, reply_markup=ads_keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('enable_ads_'))
def enable_ads_callback(call):
    chat_id = call.data[11:]

    chat_settings[chat_id] = {'ads_enabled': True, 'activity_level': 3}

    enable_message = "Удаление сообщений содержащих ссылку включено ✅"

    back_keyboard = telebot.types.InlineKeyboardMarkup()
    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data=f"back_to_chat_{chat_id}")
    back_keyboard.add(back_button)

    bot.send_message(call.message.chat.id, enable_message, reply_markup=back_keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('disable_ads_'))
def disable_ads_callback(call):
    chat_id = call.data[12:]

    chat_settings[chat_id] = {'ads_enabled': False, 'activity_level': 3}

    disable_message = "Удаление сообщений содержащих ссылку отключено ⛔"

    back_keyboard = telebot.types.InlineKeyboardMarkup()
    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data=f"back_to_chat_{chat_id}")
    back_keyboard.add(back_button)

    bot.send_message(call.message.chat.id, disable_message, reply_markup=back_keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('set_activity_'))
def set_activity_callback(call):
    data = call.data[13:]
    chat_id, activity_level = data.rsplit('_', 1)

    if chat_id in chat_settings:
        chat_settings[chat_id]['activity_level'] = int(int(activity_level) / 20)
        print(f"Установлена активность {chat_settings[chat_id]['activity_level']} для чата {chat_id}")

    activity_text = f"Активность бота в вашем чате - {activity_level} 📊"

    back_keyboard = telebot.types.InlineKeyboardMarkup()
    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data=f"back_to_chat_{chat_id}")
    back_keyboard.add(back_button)

    bot.send_message(call.message.chat.id, activity_text, reply_markup=back_keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('back_to_chat_'))
def back_to_chat_callback(call):
    user_id = call.from_user.id

    if user_id in user_states:
        chat_name = user_states[user_id].get('chat_name', "Неизвестный чат")
        chat_id = user_states[user_id].get('chat_id')
    else:
        chat_name = "Неизвестный чат"
        chat_id = None

    chat_keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    activity_button = telebot.types.InlineKeyboardButton(text="📊 Активность бота", callback_data=f"activity_{chat_id}")
    ads_button = telebot.types.InlineKeyboardButton(text="📛 Реклама в чате", callback_data=f"ads_{chat_id}")
    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data='back_to_chatlist')

    chat_keyboard.add(activity_button)
    chat_keyboard.add(ads_button)
    chat_keyboard.add(back_button)

    if chat_id is not None:
        bot.send_message(call.message.chat.id, f"Вы выбрали чат \"{chat_name}\" 📣\n\nВыберите одну из кнопок ниже:",
                        reply_markup=chat_keyboard)
    else:
        bot.send_message(call.message.chat.id, "Произошла ошибка при получении информации о чате.", reply_markup=chat_keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'back_to_chatlist')
def back_to_chatlist_callback(call):
    chats_callback(call)

@bot.message_handler(content_types=['text', 'sticker', 'photo', 'animation'])
def handle_messages(message):
    if str(message.chat.id) in chat_settings and chat_settings[str(message.chat.id)]['ads_enabled']:
        if contains_link(message):
            try:
                bot.delete_message(message.chat.id, message.message_id)
                bot.send_message(message.chat.id, AD_MESSAGE)
                print(f"Удалено сообщение со ссылкой в чате {message.chat.id}")
                return
            except Exception as e:
                print(f"Ошибка при удалении сообщения: {e}")
                return

    save_message(message)

    if message.chat.type != 'private':
        chat_id = str(message.chat.id)
        if chat_id in chat_settings:
            activity_level = chat_settings[chat_id]['activity_level']
        else:
            activity_level = 3

        random_number = random.randint(0, 100)

        if random_number <= activity_level * 20:
            choice = random.randint(1, 100)

            if choice <= 20:
                gif_file_id = get_random_media(message.chat.id, 'animation')
                if gif_file_id:
                    try:
                        bot.send_animation(message.chat.id, gif_file_id)
                    except Exception as e:
                        print(f"Ошибка при отправке GIF: {e}")
            elif 20 < choice <= 40:
                photo_file_id = get_random_media(message.chat.id, 'photo')
                if photo_file_id:
                    try:
                        bot.send_photo(message.chat.id, photo_file_id)
                    except Exception as e:
                        print(f"Ошибка при отправке фото: {e}")
            elif 40 < choice <= 60:
                random_message = get_random_message()
                if random_message and random_message[0] == 'sticker':
                    try:
                        bot.send_sticker(message.chat.id, random_message[1])
                    except Exception as e:
                        print(f"Ошибка при отправке стикера: {e}")
            else:
                random_message = get_random_message()
                if random_message and random_message[0] == 'text':
                    try:
                        bot.send_message(message.chat.id, random_message[1])
                    except Exception as e:
                        print(f"Ошибка при отправке текста: {e}")

@bot.callback_query_handler(func=lambda call: True)
def callback_query_handler(call):
    pass

@bot.message_handler(content_types=['new_chat_members'])
def new_member(message):
    if message.new_chat_members[0].id == bot.get_me().id:
        bot.send_message(message.chat.id, "Спасибо, что добавили меня! Не забудьте выдать мне права администратора.")

if __name__ == '__main__':
    bot.infinity_polling()