import speech_recognition as sr
from googletrans import Translator
import telebot
from telebot import types
import time
import subprocess
import os

r = sr.Recognizer()
translator = Translator()
bot = telebot.TeleBot('YOUR_BOT_TOKEN')
words_easy = ['Привет', 'Волк', 'Вода', 'Дом', 'Чай']
words_middle = ['Пока', 'Энергия', 'Дождь', 'Блокнот', 'Дверь', 'Улица']
words_hard = ['Часы', 'Компьютер', 'Звук', 'Стул', 'Кофе', 'Велосипед', 'Кровать']
score = 0
yes = 0
yes1 = 0

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет! Это игра на знание английского! Тебе будут выводится слова, а ты должен сказать это слово в голосовое сообщение по английски.')
    time.sleep(1)
    markup = types.InlineKeyboardMarkup()
    easy = types.InlineKeyboardButton(text="Лёгкий", callback_data="w_easy")
    middle = types.InlineKeyboardButton(text="Средний", callback_data="w_middle")
    hard = types.InlineKeyboardButton(text="Сложный", callback_data="w_hard")
    markup.add(easy, middle, hard)
    bot.send_message(message.chat.id, 'Но перед этим выбери уровень сложности:', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('w_'))
def easy(call):
    lvl = call.data.split('_')[1]
    lvl = globals()['words_' + lvl]
    print(lvl)
    for i in lvl:
        bot.send_message(call.message.chat.id, f'Слово: {i}')
        global translated
        translated = translator.translate(i, dest='en')
        print(translated)
        bot.send_message(call.message.chat.id, "Жду ваше голосовое сообщение...")
        bot.register_next_step_handler(call.message, fun)
        wait_true()
    bot.send_message(call.message.chat.id, f'Игра окончена! Ваш счёт: {score}')

def wait_true():
    global yes1
    while True:
        if yes > yes1:
            yes1 += 1
            return
        else:
            time.sleep(1)

def fun(message):
    if not message.voice:
        bot.register_next_step_handler(message, fun)
    f = bot.get_file(message.voice.file_id)
    f_d = bot.download_file(f.file_path)
    with open(f'filename.ogg', 'wb') as f2:
        f2.write(f_d)
    subprocess.call(['ffmpeg', '-i', r'C:\Users\nikit\Desktop\Eng\filename.ogg',
                   r'C:\Users\nikit\Desktop\Eng\filename1.wav'])
    try:
        with sr.AudioFile(r'C:\Users\nikit\Desktop\Eng\filename1.wav') as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data, language="en-EN")
            os.remove(r'C:\Users\nikit\Desktop\Eng\filename1.wav')
            text = text[0].upper() + text[1:]
        bot.send_message(message.chat.id, f"Вы сказали: {text}")
        if text == translated.text:
            bot.send_message(message.chat.id, f'Молодец! Вы сказали: {translated.text}')
            bot.send_message(message.chat.id, 'Вам начислились 10 баллов!')
            global score
            score += 10
            global yes
            yes += 1
        else:
            bot.send_message(message.chat.id, 'Неправильно!')
            yes += 1
    except sr.UnknownValueError:
        bot.send_message(message.chat.id, "Не удалось распознать речь")
        bot.register_next_step_handler(message, fun)
    except sr.RequestError:
        bot.send_message(message.chat.id, "Ошибка подключения к сервису")
        bot.register_next_step_handler(message, fun)
# print(f'Игра окончена! Ваш счёт: {score}')

bot.polling()
