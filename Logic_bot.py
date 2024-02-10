import telebot
import json
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, Message  #импорт нужных классов
from info_logictest import survey
from config import TOKEN

# адрес бота в телеграмм
#@Logic_testBot

bot = telebot.TeleBot(TOKEN, parse_mode='HTML')

# Функция сохранения информации о пользователе (словаре user_data) в файл json с параметрами
def save_user_data(user_id, user_data):
    with open(f"{user_id}_data.json", "w", encoding='utf8') as file:
        json.dump(user_data, file, ensure_ascii=False, indent=2)

# Функция сохранения информации о пользователе (словаре user_data) в файл json
def save_user_data(user_data):
    with open("user_data.json", "w", encoding='utf8') as file:
        json.dump(user_data, file, ensure_ascii=False, indent=2)

# Функция загрузки данных о пользователях из json файла в словарь user_data с параметрами
def load_user_data(user_id):
    try:
        with open(f"{user_id}_data.json", "r+", encoding='utf8') as file:
            return json.load(file)
    except:
        return {}

# Функция загрузки данных о пользователях из json файла в словарь user_data
def load_user_data():
    try:
        with open("user_data.json", "r+", encoding='utf8') as file:
            return json.load(file)
    except:
        return {}


# Проверяем наличие файла с данными пользователей и если он есть, то считываем из него значения в переменную user_data
try:
    file_with_json = open('user_data.json', 'r+', encoding='utf8')  # Открываем файл
    try:
        user_data_file = json.load(file_with_json)  # Считываем содержимое в словарь
        user_data = user_data_file # Если в файле есть записи данных о пользователях, то передаем их в словарь user_data
        print('Начальное значение user_data_file: ', user_data_file)
    except json.decoder.JSONDecodeError as err:
        user_data = {} # Изначально пользователей нет, пустой словарь
        print('Начальное значение user_data_file: пустой файл')
    file_with_json.close()  # Закрываем файл
except FileNotFoundError:
    user_data = {}
    print('Файл user_data.json ещё не создан!')


print('Начальное значение user_data:', user_data)


# Кнопки
#markup = ReplyKeyboardMarkup(resize_keyboard=True) # заготовка для клавиатуры
#markup.add(KeyboardButton('Первый текст на кнопочке')) # добавляем кнопку
#markup.add(KeyboardButton('Второй текст на кнопочке'))

@bot.message_handler(commands=['start'])
def hello_message(message): # Функция для обработки сообщений
    global user_data
    user_id = str(message.from_user.id)  # Получаем `user_id` пользователя, переводим в str, чтобы потом использовать в json формате

    # Запоминаем ползователей в словарь
    # Проверяем, что user_id пользователя есть в словаре
    # Если нет -- записываем
    if user_id in user_data:
        print(f"Пользователь {user_data[user_id]} есть в моей базе!")
    else:
        user_data[(user_id)] = {}
        print(f"Пользователя {user_id} нет в словаре")
        user_data[user_id]['user_name'] = message.from_user.username
        user_data[user_id]['user_firstname'] = message.from_user.first_name
        user_data[user_id]['user_lastname'] = message.from_user.last_name
        user_data[user_id]['question_number'] = str(0)
        user_data[user_id]['total_score'] = str(0)
        print(f"Отлично, я его {user_data[user_id]} запомнил!")
        #записываем данные user_data в файл в json формате
        file_for_json = open('user_data.json', 'w', encoding='utf8')  # Открываем файл file_name.json на чтение и запись.При открытии указывается кодировка utf8
        json.dump(user_data, file_for_json, ensure_ascii=False, indent=2)  # Записываем в него словарь в JSON-формате, разрешив нестандартные символы
        file_for_json.close()  # Закрываем файл

    print(f'Итоговый словарь: {user_data}')

    # задаем кнопку клавиатуры "Викторина", для ее запуска
    murkup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    murkup.add("Викторина")
#    murkup.add("Продолжить викторину")  # Кнопка не нужна на старте

    #    bot.send_photo(message.chat.id, photo=open('./foto/stiсker/ginger_eyes.jpg', 'rb'))
    bot.send_message(message.chat.id, f"<strong>Привет, {message.from_user.first_name}!</strong>")  # Приветствуем пользовавтеля
    bot.send_message(message.chat.id, f"<strong>Это тг-бот</strong> 🤖 @Logic_testBot !\n"
                                      f"Тут можно пройти тест и проверить своё логическое мышление!\n"
                                      f"Хочешь пройти тестирование? Жми кнопку 'Викторина'",
                                        reply_markup=murkup)  # Отправка ответа бота и вывод кнопки "Викторина"


#----------------------------------------------------------------------
# СОБСТВЕННО ВИКТОРИНА

# Функция выводящая вопрос и варианты ответа на него
# конкретному пользователю для его конкретного прогресса (т.е. вопроса на котором он остановился)
def send_question(chat_id):
    global user_data
    global question_number
    question_number = int(user_data[str(chat_id)]['question_number'])

    # Выводим текст вопроса
    bot.send_message(chat_id, f'<strong>{survey[question_number]["number"]}). {survey[question_number]["question"]}</strong>')

    # Выводим варианты ответов на заданный вопрос
    murkup = ReplyKeyboardMarkup(resize_keyboard=True)
    button_list = [KeyboardButton(f'{answer}') for answer in survey[question_number]["answers"]]
    murkup.add(*button_list)
    for answer in survey[question_number]["answers"]:
        bot.send_message(chat_id, f'<strong>{answer}</strong>: <i>{survey[question_number]["answers"][answer]["text"]}</i>', reply_markup=murkup)


# Обработчик получения ответа пользователя
@bot.message_handler(func=lambda message: True)
def logic_test(message):
    global user_data
    global total_score
    global question_number

    chat_id = str(message.from_user.id)
    if chat_id not in user_data:
        bot.send_message(chat_id, "Пожалуйста, начните Тестирование с помощью команды /start")
        return

    if message.text.lower() == "викторина" or message.text.lower() == "попробовать ещё раз?":
        total_score = 0   # Заводим счётчик
        user_data[chat_id]['total_score'] = str(total_score)
        user_data[chat_id]['question_number'] = 0
        send_question(chat_id)
    elif message.text.lower() == "продолжить викторину":
        user_data = load_user_data()  # загрузка всего json файла (всех пользователей)
        send_question(chat_id)        # загрузка вопроса на котором остановился пользователь
        total_score = int(user_data[chat_id]['total_score'])  # Считываем счетчик из данных пользователя


#-------
#--------
#----------

    question_number = int(user_data[chat_id]['question_number'])
    answers = survey[question_number]["answers"]
    if message.text not in answers:
        bot.send_message(chat_id, f"Пожалуйста, выберите или напишите один из предложенных вариантов."
                                  f"Или нажмите /start для перехода в начало теста.")
        return

    total_score = int(user_data[chat_id]['total_score'])  # Считываем счетчик из данных пользователя, на случай пропадания сети или падения сервера
    total_score += int(survey[question_number]["answers"][message.text]["score"])
    user_data[chat_id]['question_number'] = int(user_data[chat_id]['question_number']) + 1

    user_data[chat_id]['total_score'] = str(total_score)  # обновленный данные очков для записи прогресса пользователя в json файл

    if question_number < (len(survey)-1):
        save_user_data(user_data) # сохраняем данные пользователя после каждого ответа на вопрос в json
        send_question(chat_id)    # выводим вопросы для пользователя
    else:
        bot.send_message(chat_id, f'<strong>🤖 Всё!</strong>')
        # Выводим количество баллов в конце анкеты
        bot.send_message(message.chat.id, f"<strong>Вы набрали {total_score} баллов.</strong>")
#        # Выводим категорию, в которую попал пользователь
        if total_score >= 10:
            bot.send_message(message.chat.id, f"<strong>Великолепный результат!\nВаша способность делать правильные логические выводы просто потрясающа.\nВам по зубам практически любой «крепкий орешек».</strong>")
        elif 5 <= total_score <= 9:
            bot.send_message(message.chat.id, "<strong>С логикой у вас все хорошо.\nОднако порой вам трудно найти решение трудного, нестандартного вопроса.</strong>")
        else:
            bot.send_message(message.chat.id, "<strong>К сожалению, логическое мышление у вас практически не развито.\nНо не стоит отчаиваться.\nРаботайте над собой и тогда обязательно достигнете успеха.</strong>")

        murkup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        murkup.add("Попробовать ещё раз?")
        bot.send_message(message.chat.id, f"Хотите пройти тестирование ещё раз? Тогда нажмите кнопку или пришлите слово: Викторина.",
                             reply_markup=murkup)  # Отправка ответа бота и вывод кнопки "Викторина"


bot.polling(non_stop=True)



