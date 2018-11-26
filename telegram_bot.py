#!/usr/bin/env python
import telebot
import os
import redis
import json
from collections import defaultdict

bot = telebot.TeleBot(os.environ.get('TELEGRAM_BOT_TOKEN'))


r = redis.from_url(os.environ.get("REDIS_URL"))


START, NAME, LOCATION, PHOTO = range(4)
START, RESET = range(2)
USER_STATE = defaultdict(lambda: START)
USER_STATE2 = defaultdict(lambda: START)

def get_state(message):
    return USER_STATE[message.chat.id]
def update_state(message, state):
    USER_STATE[message.chat.id] = state

def get_state2(message):
    return USER_STATE2[message.chat.id]
def update_state2(message, state):
    USER_STATE2[message.chat.id] = state


if r.exists('LOCATIONS'):
    read_dict = r.get('LOCATIONS')
    LOCATIONS = json.loads(read_dict)
else:
    LOCATIONS = dict()

def get_locations(user_id):
    user_id = str(user_id)
    if user_id not in LOCATIONS:
        return {}
    else:
        return LOCATIONS[user_id]["location"]

def update_location(user_id, key, value):
    user_id = str(user_id)
    LOCATIONS[user_id]["location"][-1][key] = value

def add_location(user_id, key, value):
    user_id = str(user_id)
    if user_id not in LOCATIONS:
        LOCATIONS[user_id] = dict()
        LOCATIONS[user_id]["location"] = []
    LOCATIONS[user_id]["location"].append(dict())
    LOCATIONS[user_id]["location"][-1]["id"] = len(LOCATIONS[user_id]["location"])
    update_location(user_id, key, value)

def delete_locations(user_id):
    user_id = str(user_id)
    LOCATIONS.pop(user_id, None)

def save_base():
    json_dict = json.dumps(LOCATIONS)
    r.set('LOCATIONS', json_dict)

def closest_location(location):
    lat = location.latitude
    lon = location.longitude
    closest_lat, closest_lon = 55.72463, 37.4668071
    return closest_lat, closest_lon


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, text=("BestLocationsBot позволяет сохранить любимые места для будущего посещения.\n\n"
                                            "Отправь /add, чтобы добавить любимое место, "
                                            "/list - чтобы посмотреть список последних сохраненных мест. "
                                            "А если ты захочешь стереть все места, то отправь /reset."))


@bot.message_handler(commands=['add'])
def handle_message(message):
    bot.send_message(message.chat.id, text="Напишите название места")
    update_state(message, NAME)


@bot.message_handler(func=lambda message: get_state(message) == NAME)
def handle_name(message):
    add_location(message.chat.id, 'name', message.text)
    bot.send_message(message.chat.id, text="Отправьте локацию места")
    update_state(message, LOCATION)


@bot.message_handler(func=lambda message: get_state(message) == LOCATION, content_types='location')
def handle_location(message):
    update_location(message.chat.id, 'latitude', message.location.latitude)
    update_location(message.chat.id, 'longitude', message.location.longitude)
    # # bot.send_message(message.chat.id, text="Сделайте фото места")
    save_base()
    bot.send_message(message.chat.id, text="Готово! Любимое место сохранено")
    # update_state(message, PHOTO)
    update_state(message, START)


@bot.message_handler(commands=['list'])
def handle_list(message):
    loc_dict = get_locations(message.chat.id)
    if loc_dict != {}:
        for loc in loc_dict[::-1]:
            bot.send_message(message.chat.id, text=loc['name'])
            bot.send_location(message.chat.id, loc['latitude'], loc['longitude'])
    else:
        bot.send_message(message.chat.id, text="Вы пока ничего не добавили. Начните добавлять места набрав /add")


@bot.message_handler(commands=['reset'])
def handle_reset(message):
    bot.send_message(message.chat.id, text="Вы действительно хотите удалить все сохраненные места?")
    update_state2(message, RESET)


@bot.message_handler(func=lambda message: get_state2(message) == RESET)
def handle_reset_final(message):
    if 'да' in message.text.lower():
        delete_locations(message.chat.id)
        save_base()
        bot.send_message(message.chat.id, text="Сохраненные места удалены")
    update_state2(message, START)



# @bot.message_handler(func=lambda message: get_state(message) == PHOTO)
# @bot.message_handler(content_types='photo')
# def handle_message(message):
#     update_location(message.chat.id, 'photo', message.)
#     bot.send_message(message.chat.id, text="Готово! Любимое место сохранено")
    # lat, lon = closest_location(message.location)
    # bot.send_location(message.chat.id, lat, lon)
bot.polling()

# python3.6 -m pip freeze requirements.txt
