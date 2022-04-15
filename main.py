import telebot
import requests
import sqlite3
import os
from difflib import SequenceMatcher
from telebot import types
from image_ot_qr import QR_Operation
from Speech_rec import Recognition
from data import db_session
from data.songs import Song


with open("API_KEY", "r") as f:
    __KEY__ = f.readline()

db_session.global_init("db/musik.db")
URL = "https://api.telegram.org/bot"
bot = telebot.TeleBot(__KEY__)

users_step = {}

find_musick = types.KeyboardButton("Найти музыку")
add_musick = types.KeyboardButton("Добавить музыку")
speech = types.KeyboardButton("Голос")
text = types.KeyboardButton("Текст")
back_button = types.KeyboardButton("Назад")
qr_button = types.KeyboardButton("QR код")
rus = types.KeyboardButton("Русский")
eng = types.KeyboardButton("Английский")

@bot.message_handler(content_types=["text", "start"])
def main(message):

    if not message.from_user.id in users_step:
        users_step[message.from_user.id] = "home"

    if (message.text == "/start" or message.text == "Назад"):

        users_step[message.from_user.id] = "home"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(find_musick, add_musick)
        bot.send_message(message.chat.id,
                         text="Привет, {0.first_name}! Я тестируюсь".format(message.from_user), reply_markup=markup)

    elif (message.text == "Добавить музыку"):

        users_step[message.from_user.id] = "musick_add"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(back_button)
        bot.send_message(message.chat.id,
                         text="{0.first_name}, Скинь сначала название, затем фото потом аудио в виде файла".format(message.from_user), reply_markup=markup)

    elif (message.text == "Найти музыку"):

        users_step[message.from_user.id] = "musick_find"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(speech, text)
        markup.row(back_button, qr_button)
        bot.send_message(message.chat.id,
                         text="{0.first_name}, Выбери формат поиска".format(message.from_user), reply_markup=markup)

    elif (message.text == "Голос"):

        users_step[message.from_user.id] = "voice"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(back_button, rus, eng)
        bot.send_message(message.chat.id,
                         text="{0.first_name}, выбери язык".format(message.from_user), reply_markup=markup)

    elif (message.text == "Русский") or (message.text == "Английский"):

        users_step[message.from_user.id] = message.text
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(back_button)
        bot.send_message(message.chat.id,
                         text="Жду голосовую".format(message.from_user), reply_markup=markup)

    elif (message.text == "Текст"):

        users_step[message.from_user.id] = "text"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(back_button)
        bot.send_message(message.chat.id,
                         text="{0.first_name}, Напиши название или часть текста песни(пока только название)".format(message.from_user),
                         reply_markup=markup)

    elif (message.text == "QR код"):

        users_step[message.from_user.id] = "qr"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(back_button)
        bot.send_message(message.chat.id,
                         text="{0.first_name}, жду qr код".format(message.from_user),
                         reply_markup=markup)

    elif users_step[message.from_user.id] == "text":
        send_message(message.chat.id, message.text, message)

    elif users_step[message.from_user.id] == "musick_add":
        users_step[message.from_user.id] = ["musick_add-image", message.text]

    print(users_step)


@bot.message_handler(content_types=['photo'])
def image(message):
    print(users_step, "image")
    if message.from_user.id in users_step:
        if users_step[message.from_user.id][0] == "musick_add-image":
            file = message.photo[-1].file_id
            users_step[message.from_user.id].append(str(file))
            users_step[message.from_user.id][0] = "musick_add-file"
        elif users_step[message.from_user.id] == "qr":
            file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            src = 'nontime/' + message.photo[1].file_id + ".png"
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)
            dec = QR_Operation("nontime/" + message.photo[1].file_id)
            text_qr = dec.qr_decode()
            os.remove("nontime/" + message.photo[1].file_id + ".png")
            # Сюда нужен поиск по id
            bot.send_message(message.chat.id,
                             text=text_qr.format(
                                 message.from_user))


@bot.message_handler(content_types=['audio'])
def doc(message):
    print(users_step, "doc")
    if message.from_user.id in users_step:
        if users_step[message.from_user.id][0] == "musick_add-file":
            file = str(message.audio.file_id)
            mus = Song()
            mus.name = users_step[message.from_user.id][1]
            mus.image = users_step[message.from_user.id][2]
            mus.song = file
            mus.text = "Саша по шоссе"
            db_sess = db_session.create_session()
            db_sess.add(mus)
            db_sess.commit()
            bot.send_message(message.chat.id,
                             text="Успешно добавлено".format(
                                 message.from_user))

@bot.message_handler(content_types=['voice'])
def voice(message):
        if users_step[message.from_user.id] == "Русский":
            to_speech("ru_RU", message)
        elif users_step[message.from_user.id] == "Английский":
            to_speech("eng_ENG", message)


def to_speech(lang, message):
    filename = str(message.from_user.id)
    file_name_full = "nontime/" + filename + ".ogg"
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open(file_name_full, 'wb') as new_file:
        new_file.write(downloaded_file)
    voicer = Recognition(file_name_full, lang)
    voicer = voicer.get_audio_messages()
    send_message(message.chat.id, voicer, message)


def send_message(chat_id, name, message):
    db_sess = db_session.create_session()
    result = list(db_sess.query(Song.image, Song.song).filter(Song.name == name).distinct())
    if result:
        result = result[0]
        requests.get(f'{URL}{__KEY__}/sendPhoto?chat_id={chat_id}&photo={result[0]}&caption={name}')
        requests.get(f"{URL}{__KEY__}/sendAudio?chat_id={chat_id}&audio={result[1]}")
    else:
        song = ["", 0]
        result = list(db_sess.query(Song.text).distinct())
        for i in result:
            i = i[0]
            s = SequenceMatcher(lambda x: x == " ", name, i)
            s = s.ratio()
            if s > song[1]:
                song[1] = s
                song[0] = i
        print(song)
        result = list(db_sess.query(Song.image, Song.song, Song.name).filter(Song.text == song[0]).distinct())
        if result:
            result = result[0]
            requests.get(f'{URL}{__KEY__}/sendPhoto?chat_id={chat_id}&photo={result[0]}&caption=Совпадение {round(song[1], 1) * 100}%, {result[2]}')
            requests.get(f"{URL}{__KEY__}/sendAudio?chat_id={chat_id}&audio={result[1]}")
        else:
            bot.send_message(message.chat.id,
                             text="Ничего не нашлось... Добавь эту песню нам в коллекцию".format(
                                 message.from_user))


bot.polling(none_stop=True, interval=1)