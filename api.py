import telebot

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота, полученный от BotFather
BOT_TOKEN = '7832406550:AAGgSZ4Lh-VqMWqwijJ4-GACRYTjyt_INc8'  # Ваш токен бота

bot = telebot.TeleBot(BOT_TOKEN)

# Состояния для отслеживания шагов добавления чата
user_states = {}  # Словарь для хранения состояний пользователей

# Список чатов (заглушка)
chat_list = []

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    # Создаем inline-кнопки для главного меню
    inline_keyboard = telebot.types.InlineKeyboardMarkup()
    add_to_chat_button = telebot.types.InlineKeyboardButton(text="✏ Добавить в чат", url="https://t.me/CryptoTestPay_Bot?startgroup=true")  # Ваша ссылка для добавления
    subscribe_button = telebot.types.InlineKeyboardButton(text="✅ Подписаться на канал", url="https://t.me/+wTYMzFT9ev9iYWMy")
    support_button = telebot.types.InlineKeyboardButton(text="💰 Поддержать проект", url="http://t.me/send?start=IVY5kyjDSlsV")
    settings_button = telebot.types.InlineKeyboardButton(text="⚙ Настройки", callback_data='settings')

    inline_keyboard.add(add_to_chat_button)
    inline_keyboard.add(subscribe_button)
    inline_keyboard.add(support_button)
    inline_keyboard.add(settings_button)

    # Отправляем сообщение с кнопками и новым текстом
    start_message = "Привет!\n\nМеня зовут Игната, я бот для бесед, который на основе ваших сообщений генерирует свои собственные.\n\nДобавь меня в беседу и дай мне права администратора."
    bot.send_message(message.chat.id, start_message, reply_markup=inline_keyboard)

# Обработчик нажатия inline-кнопки "⚙ Настройки"
@bot.callback_query_handler(func=lambda call: call.data == 'settings')
def settings_callback(call):
    # Создаем inline-кнопки для меню настроек
    settings_keyboard = telebot.types.InlineKeyboardMarkup()
    add_chat_to_bot_button = telebot.types.InlineKeyboardButton(text="✏ Добавить чат в бота", callback_data='add_chat')
    delete_chat_button = telebot.types.InlineKeyboardButton(text="🗑 Удалить чат из бота", callback_data='delete_chat_menu')  # Новая кнопка
    chats_button = telebot.types.InlineKeyboardButton(text="🗂 Чаты", callback_data='chats')
    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data='back_to_main')

    settings_keyboard.add(add_chat_to_bot_button)
    settings_keyboard.add(delete_chat_button)  # Перемещаем эту кнопку выше
    settings_keyboard.add(chats_button)
    settings_keyboard.add(back_button)

    # Отправляем сообщение с кнопками настроек
    bot.send_message(call.message.chat.id, "Выберите одну из кнопок ниже:", reply_markup=settings_keyboard)

# Обработчик нажатия inline-кнопки "✏ Добавить чат в бота" (в меню настроек)
@bot.callback_query_handler(func=lambda call: call.data == 'add_chat')
def add_chat_callback(call):
    # Создаем inline-кнопки для шага 1
    add_chat_keyboard = telebot.types.InlineKeyboardMarkup()
    added_button = telebot.types.InlineKeyboardButton(text="Готово ✅", callback_data='added')  # Изменено название кнопки
    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data='back_to_settings')

    add_chat_keyboard.add(added_button)
    add_chat_keyboard.add(back_button)

    # Отправляем сообщение с кнопками
    message_step1 = "📝 Шаг 1\n\nУбедитесь, что бот добавлен в группу и у него есть права администратора! Для добавления чата необходимо иметь самому права администратора. Если бот не нашел вас в администраторах, но вы им являетесь, попробуйте убрать в настройках чата анонимность."
    bot.send_message(call.message.chat.id, message_step1, reply_markup=add_chat_keyboard)

# Обработчик нажатия inline-кнопки "Я добавил(-а)"
@bot.callback_query_handler(func=lambda call: call.data == 'added')
def added_callback(call):
    user_id = call.from_user.id
    # Отправляем сообщение для Шага 2
    message_step2 = "📝 Шаг 2\n\nОтправьте ID чата (начинается с минуса, например -123456789):"
    step2_keyboard = telebot.types.InlineKeyboardMarkup()
    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data='back_to_step1')
    step2_keyboard.add(back_button)

    bot.send_message(call.message.chat.id, message_step2, reply_markup=step2_keyboard)
    # Устанавливаем состояние пользователя на шаг 2
    user_states[user_id] = 'waiting_for_chat_id'

# Обработчик текста (ID чата)
@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == 'waiting_for_chat_id')
def handle_chat_id(message):
    user_id = message.from_user.id
    try:
        chat_id = int(message.text)  # Преобразуем текст в целое число
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, отправьте корректный ID чата (целое число, начинающееся с минуса).")
        return

    if chat_id >= 0:  # ID чата должен быть отрицательным
        bot.send_message(message.chat.id, "ID чата должен быть отрицательным (начинаться с минуса).")
        return

    try:
        # Проверяем, есть ли чат уже в списке
        if any(chat['id'] == chat_id for chat in chat_list):
            # Отправляем сообщение "Вы уже добавляли этот чат!" и кнопку "Назад"
            already_added_keyboard = telebot.types.InlineKeyboardMarkup()
            back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data='back_to_settings')
            already_added_keyboard.add(back_button)
            bot.send_message(message.chat.id, "Вы уже добавляли этот чат!", reply_markup=already_added_keyboard)
            # Сбрасываем состояние пользователя
            if user_id in user_states:
                del user_states[user_id]
            return

        # Проверяем, является ли бот администратором в чате
        chat_member = bot.get_chat_member(chat_id, bot.get_me().id)
        if chat_member.status not in ['administrator', 'creator']:
            bot.send_message(message.chat.id, "У бота нет прав администратора в этом чате!")
            return

        # Проверяем, является ли пользователь администратором в чате
        user_chat_member = bot.get_chat_member(chat_id, user_id)
        if user_chat_member.status not in ['administrator', 'creator']:
            # Отправляем сообщение об отсутствии прав администратора
            not_admin_keyboard = telebot.types.InlineKeyboardMarkup()
            back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data='back_to_settings')
            not_admin_keyboard.add(back_button)
            bot.send_message(message.chat.id, "Вы не являетесь администратором чата. Если это так, попробуйте убрать анонимность в настройках чата.", reply_markup=not_admin_keyboard)
            # Сбрасываем состояние пользователя
            if user_id in user_states:
                del user_states[user_id]
            return

        # Получаем информацию о чате (имя)
        chat_info = bot.get_chat(chat_id)
        chat_name = chat_info.title  # Получаем название чата

        # Добавляем чат в список
        chat_list.append({"id": chat_id, "name": chat_name})  # Сохраняем ID и имя

    except telebot.apihelper.ApiTelegramException as e:
        bot.send_message(message.chat.id, f"Не удалось получить имя чата: {e}")
        return

    # Если все проверки пройдены, отправляем сообщение об успехе и добавляем кнопку "Назад"
    success_keyboard = telebot.types.InlineKeyboardMarkup()
    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data='back_to_settings')
    success_keyboard.add(back_button)
    bot.send_message(message.chat.id, "Отлично, ваша группа добавлена в список чатов ✅", reply_markup=success_keyboard)

    # Сбрасываем состояние пользователя
    if user_id in user_states:
        del user_states[user_id]

# Обработчик нажатия inline-кнопки "Назад" (на шаге 1)
@bot.callback_query_handler(func=lambda call: call.data == 'back_to_step1')
def back_to_step1_callback(call):
    user_id = call.from_user.id
    # Создаем inline-кнопки для шага 1
    add_chat_keyboard = telebot.types.InlineKeyboardMarkup()
    added_button = telebot.types.InlineKeyboardButton(text="Готово ✅", callback_data='added')  # Изменено название кнопки
    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data='back_to_settings')

    add_chat_keyboard.add(added_button)
    add_chat_keyboard.add(back_button)

    # Отправляем сообщение с кнопками
    message_step1 = "📝 Шаг 1\n\nУбедитесь, что бот добавлен в группу и у него есть права администратора! Для добавления чата необходимо иметь самому права администратора. Если бот не нашел вас в администраторах, но вы им являетесь, попробуйте убрать в настройках чата анонимность."
    bot.send_message(call.message.chat.id, message_step1, reply_markup=add_chat_keyboard)
    # Сбрасываем состояние пользователя
    if user_id in user_states:
        del user_states[user_id]

# Обработчик нажатия inline-кнопки "Назад" (в меню настроек)
@bot.callback_query_handler(func=lambda call: call.data == 'back_to_main')
def back_to_main_callback(call):
    # Вызываем функцию start для возврата в главное меню
    start(call.message)

# Обработчик нажатия inline-кнопки "Назад" (возврат в меню настроек)
@bot.callback_query_handler(func=lambda call: call.data == 'back_to_settings')
def settings_callback(call):
    # Создаем inline-кнопки для меню настроек
    settings_keyboard = telebot.types.InlineKeyboardMarkup()
    add_chat_to_bot_button = telebot.types.InlineKeyboardButton(text="✏ Добавить чат в бота", callback_data='add_chat')
    delete_chat_button = telebot.types.InlineKeyboardButton(text="🗑 Удалить чат из бота", callback_data='delete_chat_menu')  # Новая кнопка
    chats_button = telebot.types.InlineKeyboardButton(text="🗂 Чаты", callback_data='chats')
    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data='back_to_main')

    settings_keyboard.add(add_chat_to_bot_button)
    settings_keyboard.add(delete_chat_button)  # Перемещаем эту кнопку выше
    settings_keyboard.add(chats_button)
    settings_keyboard.add(back_button)

    # Отправляем сообщение с кнопками настроек
    bot.send_message(call.message.chat.id, "Выберите одну из кнопок ниже:", reply_markup=settings_keyboard)

# Обработчик нажатия на кнопку "Удалить чат из бота"
@bot.callback_query_handler(func=lambda call: call.data == 'delete_chat_menu')
def delete_chat_menu_callback(call):
    # Проверяем, есть ли чаты для удаления
    if not chat_list:
        no_chats_keyboard = telebot.types.InlineKeyboardMarkup()
        back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data='back_to_settings')
        no_chats_keyboard.add(back_button)
        bot.send_message(call.message.chat.id, "Список чатов пуст. Нечего удалять.", reply_markup=no_chats_keyboard)
        return

    # Создаем клавиатуру со списком чатов для удаления
    delete_chat_keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    for chat in chat_list:
        delete_button = telebot.types.InlineKeyboardButton(text=chat["name"], callback_data=f"confirm_delete_{chat['id']}")
        delete_chat_keyboard.add(delete_button)

    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data='back_to_settings')
    delete_chat_keyboard.add(back_button)

    # Отправляем сообщение с кнопками для выбора чата
    bot.send_message(call.message.chat.id, "Выберите чат, который хотите удалить из бота:", reply_markup=delete_chat_keyboard)

# Обработчик подтверждения удаления чата
@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_delete_'))
def confirm_delete_callback(call):
    chat_id = call.data[15:]  # Извлекаем ID чата из callback_data

    # Находим имя чата по ID
    chat_name = ""
    for chat in chat_list:
        if str(chat['id']) == chat_id:
            chat_name = chat['name']
            break

    # Создаем клавиатуру для подтверждения удаления
    confirm_keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    yes_button = telebot.types.InlineKeyboardButton(text="Да ✅", callback_data=f"delete_{chat_id}")
    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data='delete_chat_menu')
    confirm_keyboard.add(yes_button)
    confirm_keyboard.add(back_button)

    # Отправляем сообщение для подтверждения удаления
    bot.send_message(call.message.chat.id, f"Вы точно хотите удалить чат \"{chat_name}\"?", reply_markup=confirm_keyboard)

# Обработчик удаления чата
@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_'))
def delete_callback(call):
    chat_id = call.data[7:]  # Извлекаем ID чата из callback_data

    # Находим имя чата по ID для сообщения об успешном удалении
    chat_name = ""
    for chat in chat_list:
        if str(chat['id']) == chat_id:
            chat_name = chat['name']
            break

    # Удаляем чат из списка
    chat_list[:] = [chat for chat in chat_list if str(chat['id']) != chat_id]  # Удаляем из списка

    # Отправляем сообщение об успешном удалении и кнопку "Назад"
    success_keyboard = telebot.types.InlineKeyboardMarkup()
    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data='back_to_settings')  # возврат в настройки
    success_keyboard.add(back_button)
    bot.send_message(call.message.chat.id, f"Чат \"{chat_name}\" успешно удален ✅", reply_markup=success_keyboard)

# Обработчик нажатия inline-кнопки "🗂 Чаты"
@bot.callback_query_handler(func=lambda call: call.data == 'chats')
def chats_callback(call):
    # Создаем inline-клавиатуру для отображения списка чатов
    chats_keyboard = telebot.types.InlineKeyboardMarkup(row_width=1) # Чтобы кнопки были в столбик

    if not chat_list:
        # Отправляем сообщение "Список чатов пуст." и кнопку "Назад"
        empty_keyboard = telebot.types.InlineKeyboardMarkup()
        back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data='back_to_settings')
        empty_keyboard.add(back_button)
        bot.send_message(call.message.chat.id, "Список чатов пуст.", reply_markup=empty_keyboard)

        return

    # Добавляем кнопки для каждого чата
    for chat in chat_list:
        chat_button = telebot.types.InlineKeyboardButton(text=chat["name"], callback_data=f"chat_{chat['id']}")  # Используем ID для callback_data
        chats_keyboard.add(chat_button)

    # Добавляем кнопку "Назад"
    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data='back_to_settings')
    chats_keyboard.add(back_button)

    # Отправляем сообщение с кнопками чатов
    bot.send_message(call.message.chat.id, "Выберите чат:", reply_markup=chats_keyboard)

# Обработчик нажатия на кнопку чата (здесь нужно реализовать действия при выборе чата)
@bot.callback_query_handler(func=lambda call: call.data.startswith('chat_'))
def chat_button_callback(call):
    chat_id = call.data[5:]  # Извлекаем ID чата из callback_data (убираем "chat_")
    user_id = call.from_user.id

    # Получаем информацию о чате, чтобы получить имя
    selected_chat = next((chat for chat in chat_list if str(chat['id']) == chat_id), None)
    if selected_chat:
        chat_name = selected_chat["name"]
        # Сохраняем chat_id в user_states для данного пользователя
        user_states[user_id] = user_states.get(user_id, {})
        user_states[user_id]['chat_id'] = chat_id
    else:
        chat_name = "Неизвестный чат"  # Обработка случая, если чат не найден

    # Создаем inline-клавиатуру для выбранного чата
    chat_keyboard = telebot.types.InlineKeyboardMarkup(row_width=1) # Кнопки в столбик
    activity_button = telebot.types.InlineKeyboardButton(text="📊 Активность бота", callback_data=f"activity_{chat_id}")
    ads_button = telebot.types.InlineKeyboardButton(text="📛 Реклама в чате", callback_data=f"ads_{chat_id}")
    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data='back_to_chatlist')

    chat_keyboard.add(activity_button)
    chat_keyboard.add(ads_button)
    chat_keyboard.add(back_button)

    # Отправляем сообщение с кнопками для выбранного чата
    bot.send_message(call.message.chat.id, f"Вы выбрали чат \"{chat_name}\" 📣\n\nВыберите одну из кнопок ниже:", reply_markup=chat_keyboard)

# Обработчик нажатия на кнопку "Активность бота"
@bot.callback_query_handler(func=lambda call: call.data.startswith('activity_'))
def activity_callback(call):
    chat_id = call.data[9:]  # Извлекаем ID чата из callback_data (убираем "activity_")
    user_id = call.from_user.id

    # Получаем имя чата из user_states
    chat_name = "Неизвестный чат"
    if user_id in user_states and 'chat_id' in user_states[user_id]:
        selected_chat_id = user_states[user_id]['chat_id']
        selected_chat = next((chat for chat in chat_list if str(chat['id']) == selected_chat_id), None)
        if selected_chat:
            chat_name = selected_chat["name"]

    # Текст сообщения
    activity_message = "1 - 20 % активность\n" \
                       "2 - 40 % активность\n" \
                       "3 - 60 % активность\n" \
                       "4 - 80 % активность\n" \
                       "5 - 100 % активность\n\n" \
                       "Выберите активность бота в вашем чате:"

    # Создаем клавиатуру с уровнями активности
    activity_keyboard = telebot.types.InlineKeyboardMarkup(row_width=5)
    btn1 = telebot.types.InlineKeyboardButton(text="1", callback_data=f"set_activity_{chat_id}_20")
    btn2 = telebot.types.InlineKeyboardButton(text="2", callback_data=f"set_activity_{chat_id}_40")
    btn3 = telebot.types.InlineKeyboardButton(text="3", callback_data=f"set_activity_{chat_id}_60")
    btn4 = telebot.types.InlineKeyboardButton(text="4", callback_data=f"set_activity_{chat_id}_80")
    btn5 = telebot.types.InlineKeyboardButton(text="5", callback_data=f"set_activity_{chat_id}_100")
    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data=f"back_to_chat_{chat_id}")

    activity_keyboard.add(btn1, btn2, btn3, btn4, btn5)  # Кнопки в один ряд
    activity_keyboard.add(back_button) # Кнопка назад под уровнями активности

    bot.send_message(call.message.chat.id, activity_message, reply_markup=activity_keyboard)

# Обработчик нажатия на кнопку "Реклама в чате"
@bot.callback_query_handler(func=lambda call: call.data.startswith('ads_'))
def ads_callback(call):
    chat_id = call.data[4:]  # Извлекаем ID чата из callback_data (убираем "ads_")
    user_id = call.from_user.id

    # Получаем имя чата из user_states
    chat_name = "Неизвестный чат"
    if user_id in user_states and 'chat_id' in user_states[user_id]:
        selected_chat_id = user_states[user_id]['chat_id']
        selected_chat = next((chat for chat in chat_list if str(chat['id']) == selected_chat_id), None)
        if selected_chat:
            chat_name = selected_chat["name"]
    # Текст сообщения
    ads_message = "Если включить эту функцию, то бот будет удалять все сообщения с ссылками 📛.\n\nВыберите одну из кнопок ниже:"

    # Создаем клавиатуру для включения/выключения рекламы
    ads_keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    enable_button = telebot.types.InlineKeyboardButton(text="Включить ✅", callback_data=f"enable_ads_{chat_id}")
    disable_button = telebot.types.InlineKeyboardButton(text="Выключить ⛔", callback_data=f"disable_ads_{chat_id}")
    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data=f"back_to_chat_{chat_id}")

    ads_keyboard.add(enable_button, disable_button)
    ads_keyboard.add(back_button)

    bot.send_message(call.message.chat.id, ads_message, reply_markup=ads_keyboard)

# Обработчик включения рекламы
@bot.callback_query_handler(func=lambda call: call.data.startswith('enable_ads_'))
def enable_ads_callback(call):
    chat_id = call.data[11:]  # Извлекаем ID чата из callback_data (убираем "enable_ads_")
    user_id = call.from_user.id
    # Получаем имя чата из user_states
    chat_name = "Неизвестный чат"
    if user_id in user_states and 'chat_id' in user_states[user_id]:
        selected_chat_id = user_states[user_id]['chat_id']
        selected_chat = next((chat for chat in chat_list if str(chat['id']) == selected_chat_id), None)
        if selected_chat:
            chat_name = selected_chat["name"]
    enable_message = "Все сообщения содержащие ссылку будут удаляться ✅"

    # Клавиатура для возврата в меню чата
    back_keyboard = telebot.types.InlineKeyboardMarkup()
    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data=f"back_to_chat_{chat_id}")
    back_keyboard.add(back_button)

    bot.send_message(call.message.chat.id, enable_message, reply_markup=back_keyboard)

# Обработчик выключения рекламы
@bot.callback_query_handler(func=lambda call: call.data.startswith('disable_ads_'))
def disable_ads_callback(call):
    chat_id = call.data[12:]  # Извлекаем ID чата из callback_data (убираем "disable_ads_")
    user_id = call.from_user.id

    # Получаем имя чата из user_states
    chat_name = "Неизвестный чат"
    if user_id in user_states and 'chat_id' in user_states[user_id]:
        selected_chat_id = user_states[user_id]['chat_id']
        selected_chat = next((chat for chat in chat_list if str(chat['id']) == selected_chat_id), None)
        if selected_chat:
            chat_name = selected_chat["name"]

    disable_message = "Удаление сообщений содержащих ссылку отключено ⛔"

    # Клавиатура для возврата в меню чата
    back_keyboard = telebot.types.InlineKeyboardMarkup()
    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data=f"back_to_chat_{chat_id}")
    back_keyboard.add(back_button)

    bot.send_message(call.message.chat.id, disable_message, reply_markup=back_keyboard)

# Обработчик нажатия на уровень активности
@bot.callback_query_handler(func=lambda call: call.data.startswith('set_activity_'))
def set_activity_callback(call):
    data = call.data[13:]  # убираем "set_activity_"
    chat_id, activity_level = data.rsplit('_', 1)  # Разделяем строку только один раз справа
        # Получаем имя чата для возврата в меню чата
    user_id = call.from_user.id

    activity_text = f"Активность бота в вашем чате - {activity_level} 📊"  # Замена здесь

    # Клавиатура для возврата в меню чата
    back_keyboard = telebot.types.InlineKeyboardMarkup()
    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data=f"back_to_chat_{chat_id}")
    back_keyboard.add(back_button)

    bot.send_message(call.message.chat.id, activity_text, reply_markup=back_keyboard)

# Обработчик нажатия на кнопку "Назад" (из меню чата)
@bot.callback_query_handler(func=lambda call: call.data.startswith('back_to_chat_'))
def back_to_chat_callback(call):
    user_id = call.from_user.id

    # Получаем chat_id из user_states
    chat_name = "Неизвестный чат"
    chat_id = None  # Инициализируем chat_id
    if user_id in user_states and 'chat_id' in user_states[user_id]:
        chat_id = user_states[user_id]['chat_id']  # Получаем chat_id
        selected_chat_id = user_states[user_id]['chat_id']
        selected_chat = next((chat for chat in chat_list if str(chat['id']) == selected_chat_id), None)
        if selected_chat:
            chat_name = selected_chat["name"]

    # Создаем inline-клавиатуру для выбранного чата
    chat_keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)  # Кнопки в столбик
    activity_button = telebot.types.InlineKeyboardButton(text="📊 Активность бота", callback_data=f"activity_{chat_id}")
    ads_button = telebot.types.InlineKeyboardButton(text="📛 Реклама в чате", callback_data=f"ads_{chat_id}")
    back_button = telebot.types.InlineKeyboardButton(text="Назад", callback_data='back_to_chatlist')

    chat_keyboard.add(activity_button)
    chat_keyboard.add(ads_button)
    chat_keyboard.add(back_button)

    # Отправляем сообщение с кнопками для выбранного чата
    bot.send_message(call.message.chat.id, f"Вы выбрали чат \"{chat_name}\" 📣\n\nВыберите одну из кнопок ниже:",
                    reply_markup=chat_keyboard)

# Обработчик нажатия на кнопку "Назад" (из списка чатов)
@bot.callback_query_handler(func=lambda call: call.data == 'back_to_chatlist')
def back_to_chatlist_callback(call):
    chats_callback(call)  # Возвращаемся к списку чатов

# Обработчик всех остальных callback_query (для игнорирования старых сообщений)
@bot.callback_query_handler(func=lambda call: True)
def callback_query_handler(call):
    # Игнорируем все остальные callback_query
    pass

# Запускаем бота
@bot.message_handler(content_types=['new_chat_members'])
def new_member(message):
    # Если бота добавили в группу, отправляем сообщение
    if message.new_chat_members[0].id == bot.get_me().id:
        bot.send_message(message.chat.id, "Спасибо, что добавили меня! Не забудьте выдать мне права администратора.")

if __name__ == '__main__':
    bot.polling(none_stop=True)