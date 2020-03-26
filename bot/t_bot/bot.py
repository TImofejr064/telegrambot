import telebot
from telebot import types
from data import *

bot = telebot.TeleBot('1100517891:AAH-oz5g8r03FRokRJfhfQj4_eUdVDSYpm4')

keyboard1 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard1.row('📝Создать заметку', '📚Все заметки')
keyboard1.row('🤖Хочу такого-же бота')

keyboard2 = telebot.types.InlineKeyboardMarkup()
url_button = types.InlineKeyboardButton(text="Я в телеграмме", url="https://t.me/Timofejr")
keyboard2.add(url_button)

headline = ''
text = ''    

def getHeadline(message):
    global headline
    headline = message.text
    bot.send_message(message.chat.id,"А теперь введите текст")
    bot.register_next_step_handler(message, getText)

def getText(message):
    global headline
    global text 
    text = message.text
    status = Status.get(Status.status == "Выполняется")
    user = User.get(User.userId==message.from_user.id, User.username==message.from_user.username)
    task = Task.create(headline=headline, text=text, status=status, user=user)
    bot.send_message(message.chat.id, "Заметка добавлена! :)")

def startAddTask(message):
    bot.send_message(message.message.chat.id, "Введите заголовок")
    bot.register_next_step_handler(message.message, getHeadline)

def getAllTasks(message, isFromKeyboard=False):
    mes = """<b>Ваши заметки:</b>\n  """
    i = 1
    user = User.get(User.userId==message.from_user.id, User.username==message.from_user.username)
    allTasks = Task.select().where(Task.user==user)
    for task in allTasks:
        headline = task.headline
        text = task.text
        tasksId = task.id

        mes += f"{i}: {headline} /s{tasksId} \n "
        i+=1

    if isFromKeyboard==True:
        bot.send_message(message.message.chat.id,mes,  parse_mode='HTML')
    else:
        bot.send_message(message.chat.id,  mes , parse_mode='HTML')

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет!', reply_markup=keyboard1)
    try:
        user = User.get(User.userid==message.from_user.id, User.username==message.from_user.username)
    except:
        user = User.create(userId=message.from_user.id, username=message.from_user.username)
    
@bot.message_handler(content_types=['text'])
def get_message(message):
    if message.text == "📝Создать заметку":
        bot.send_message(message.chat.id, "Введите заголовок")
        bot.register_next_step_handler(message, getHeadline)
    elif message.text == "📚Все заметки":
        getAllTasks(message)
    elif message.text[0:2] == "/s":
        taskId = int(message.text[2::])
        user = User.get(User.userId==message.from_user.id, User.username==message.from_user.username)
        task = Task.get(Task.user==user, Task.id==taskId)
        mes = f""" <b>{task.headline}</b> \n {task.text}"""        
        keyboard = types.InlineKeyboardMarkup()
        key_delete = types.InlineKeyboardButton(text='Удалить', callback_data=f'd{taskId}') 
        keyboard.add(key_delete)
        bot.send_message(message.chat.id, mes, parse_mode='HTML', reply_markup=keyboard)
    elif message.text == "🤖Хочу такого-же бота":
        bot.send_message(message.chat.id, "Пишите мне в телеграм, если хотите себе бота в телеграм", reply_markup=keyboard2)

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data[0] == "d":
        user = User.get(User.userId==call.from_user.id, User.username==call.from_user.username)
        taskId = call.data[1::]
        task = Task.get(Task.user==user, Task.id==taskId)
        task.delete_instance()
        keyboard = types.InlineKeyboardMarkup()
        key_delete = types.InlineKeyboardButton(text='Назад', callback_data="Все заметки") 
        keyboard.add(key_delete)
        key_add = types.InlineKeyboardButton(text='Добавть заметку', callback_data="Добавить заметку") 
        keyboard.add(key_add)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, inline_message_id=call.inline_message_id, reply_markup=keyboard)    
    elif call.data == "Все заметки":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        getAllTasks(call, isFromKeyboard=True)
    elif call.data == "Добавить заметку":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        startAddTask(call)

bot.polling(none_stop=True)
