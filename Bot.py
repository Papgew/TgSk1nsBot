import telebot
import psycopg2
from psycopg2 import sql
from telebot import types

bot = telebot.TeleBot('6377358980:AAFrYLngYU_cEWlTR2jlVYelUt3nHtfWBt8')

conn_skinwallet = psycopg2.connect(dbname='projects', host='localhost', user='postgres', password='1090', client_encoding='utf8')
cursor_skinwallet = conn_skinwallet.cursor()

conn_lisskins = psycopg2.connect(dbname='projects', host='localhost', user='postgres', password='1090', client_encoding='utf8')
cursor_lisskins = conn_lisskins.cursor()

conn_skinport = psycopg2.connect(dbname='projects', host='localhost', user='postgres', password='1090', client_encoding='utf8')
cursor_skinport = conn_skinport.cursor()

# Глобальные переменные
min_price = 0
max_price = 100000000
offset = 0
liked = 0
disliked = 0

weapon_type = None
skin_name = None
wear_condition = None

weapon_types = {
    'Пистолеты': 'pistols',
    'Ножи': 'knife',
    'Перчатки': 'gloves',
    'Винтовки': 'rifle',
    'Тяжелое': 'heavy',
    'Пистолеты пулеметы': 'smg'
}

wear_conditions = {
    'Закаленный в боях': 'Battle-Scarred',
    'Поношенный': 'Well-Worn',
    'После полевых испытаний': 'Field-Tested',
    'Немного поношенный': 'Minimal Wear',
    'Прямо с завода': 'Factory new',
    'Любой износ': 'Any'
}


@bot.message_handler(commands=['start'])
def start(message):
    global offset, liked, disliked

    offset = 0
    liked = 0
    disliked = 0

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('Скины')
    button2 = types.KeyboardButton('Рандомный скин')
    button3 = types.KeyboardButton('О нас')
    markup.add(button1, button2, button3)
    bot.send_message(message.chat.id, "Здравствуйте, вас приветствует телеграмм бот по скинам из игры CSGO-CS2. Пожалуйста, выберите действие:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Рандомный скин')
def handle_random_skin(message):
    global offset, liked, disliked

    offset = 0
    liked = 0
    disliked = 0

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button4 = types.KeyboardButton('Рандом скин')
    button5 = types.KeyboardButton('+')
    button6 = types.KeyboardButton('-')
    button7 = types.KeyboardButton('Назад')

    markup.add(button4)
    markup.add(button5, button6, button7)

    bot.send_message(message.chat.id, 'Выберите пункт меню:', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Рандом скин')
def handle_random_skin(message):
    random_skin_query = f"""
    SELECT name, price, iznos, item_page, type
    FROM (
      SELECT name, price, iznos, item_page, type, row_number() OVER () AS row_num
      FROM lisskins
      WHERE price BETWEEN {min_price} AND {max_price}
    ) AS subquery
    ORDER BY random()
    LIMIT 1;
    """
    cursor_lisskins.execute(random_skin_query)
    result = cursor_lisskins.fetchone()

    if result:
        name, price, iznos, item_page, skin_type = result
        output_string = f"Name: {name}, Price: {price}, Iznos: {iznos}, Item Page: {item_page}, Type: {skin_type}"
        bot.send_message(message.chat.id, output_string)
    else:
        bot.send_message(message.chat.id, "No skins found in the specified price range.")


@bot.message_handler(func=lambda message: message.text == '+')
def handle_plus(message):
    global liked, min_price, max_price

    liked += 1
    if liked == 3:
        min_price += 15
        max_price += 15
        liked = 0

    random_skin_query = f"""
    SELECT name, price, iznos, item_page, type
    FROM (
      SELECT name, price, iznos, item_page, type, row_number() OVER () AS row_num
      FROM lisskins
      WHERE price BETWEEN {min_price} AND {max_price}
    ) AS subquery
    ORDER BY random()
    LIMIT 1;
    """
    cursor_lisskins.execute(random_skin_query)
    result = cursor_lisskins.fetchone()

    if result:
        name, price, iznos, item_page, skin_type = result
        output_string = f"Name: {name}, Price: {price}, Iznos: {iznos}, Item Page: {item_page}, Type: {skin_type}"
        bot.send_message(message.chat.id, output_string)
    else:
        bot.send_message(message.chat.id, "No skins found in the specified price range.")


@bot.message_handler(func=lambda message: message.text == '-')
def handle_minus(message):
    global disliked, min_price, max_price
    disliked += 1
    if disliked == 2:
        min_price -= 30
        max_price -= 30
        disliked = 0

    random_skin_query = f"""
    SELECT name, price, iznos, item_page, type
    FROM (
      SELECT name, price, iznos, item_page, type, row_number() OVER () AS row_num
      FROM lisskins
      WHERE price BETWEEN {min_price} AND {max_price}
    ) AS subquery
    ORDER BY random()
    LIMIT 1;
    """
    cursor_lisskins.execute(random_skin_query)
    result = cursor_lisskins.fetchone()

    if result:
        name, price, iznos, item_page, skin_type = result
        output_string = f"Name: {name}, Price: {price}, Iznos: {iznos}, Item Page: {item_page}, Type: {skin_type}"
        bot.send_message(message.chat.id, output_string)
    else:
        bot.send_message(message.chat.id, "No skins found in the specified price range.")


@bot.message_handler(func=lambda message: message.text == 'Назад')
def handle_back(message):
    start(message)



@bot.message_handler(func=lambda message: True)
def echo_message(message):
    global weapon_type, skin_name, offset, wear_condition
    if message.text == 'Скины':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton('Пистолеты')
        button2 = types.KeyboardButton('Пистолеты пулеметы')
        button3 = types.KeyboardButton('Винтовки')
        button4 = types.KeyboardButton('Тяжелое')
        button5 = types.KeyboardButton('Перчатки')
        button6 = types.KeyboardButton('Ножи')
        button7 = types.KeyboardButton('Назад')
        markup.add(button1, button2, button3, button4, button5, button6, button7)
        bot.send_message(message.chat.id, 'Выберите, пожалуйста, тип оружия о котором хотите узнать.', reply_markup=markup)
    elif message.text in weapon_types.keys():
        weapon_type = weapon_types[message.text]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        conditions_buttons = []
        for condition in wear_conditions.keys():
            conditions_buttons.append(types.KeyboardButton(condition))
        markup.add(*conditions_buttons)
        markup.add(types.KeyboardButton('Назад'))
        bot.send_message(message.chat.id, 'Выберите износ скина:', reply_markup=markup)
    elif message.text in wear_conditions.keys():
        wear_condition = wear_conditions[message.text]
        bot.send_message(message.chat.id, 'Введите название скина:')
    elif weapon_type is not None and wear_condition is not None:
        skin_name = message.text

        response = ''
        for cursor, table_name in zip([cursor_skinwallet, cursor_lisskins, cursor_skinport], ['skinwallet', 'lisskins', 'skinport']):
            if wear_condition == 'Any':
                query = sql.SQL("SELECT DISTINCT name, price, iznos, item_page, type FROM {} WHERE lower(name) LIKE {} AND lower(type) = {} LIMIT 5 OFFSET {}").format( sql.Identifier(table_name), sql.Literal('%' + skin_name.lower() + '%'), sql.Literal(weapon_type), sql.Literal(offset)
                )
            else:
                query = sql.SQL("SELECT DISTINCT name, price, iznos, item_page, type FROM {} WHERE lower(name) LIKE {} AND lower(type) = {} AND iznos = {} LIMIT 5 OFFSET {}").format( sql.Identifier(table_name), sql.Literal('%' + skin_name.lower() + '%'), sql.Literal(weapon_type), sql.Literal(wear_condition), sql.Literal(offset)
                )

            cursor.execute(query)
            results = cursor.fetchall()

            if results:
                for row in results:
                    item_info = f"{row[0]}; Цена - {row[1]}; Износ - {row[2]}; Ссылка - {row[3]}\n"
                    if len(response) + len(item_info) > 4096:
                        bot.send_message(message.chat.id, response)
                        response = item_info
                    else:
                        response += item_info

                if response:
                    bot.send_message(message.chat.id, response)
            else:
                bot.send_message(message.chat.id, f'Таблица {table_name}: Такого не найдено.')

    elif message.text == 'О нас':
        bot.send_message(message.chat.id, 'Делали Алдияр и Ернат из группы ПО2204Г.')
    elif message.text == 'Назад':
        start(message)

bot.polling()