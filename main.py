import sqlite3
import json
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

with sqlite3.connect('data.db') as db:  # creating a database and table for user's information
    cursor = db.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
    id BIGINT,
    happiness INTEGER,
    inspiration INTEGER,
    relief INTEGER,
    disinterest INTEGER,
    anxiety INTEGER,
    apathy INTEGER,
    irritation INTEGER,
    sadness INTEGER)
    """)
    db.commit()

vkbot = vk_api.VkApi(token='6023e420b6cb860a16ffee6fd5c22c58018edaa6e9e2bfa714076bdf52fb168d009cf0f4462ab8f84fc7d')
bot_api = vkbot.get_api()
longpoll = VkLongPoll(vkbot)


def get_but(text, color):  # creating a button
    return {
        "action": {
            "type": "text",
            "payload": "{\"button\": \"" + "1" + "\"}",
            "label": f"{text}"
        },
        "color": f"{color}"
    }


main_menu = {  # main keyboard
    "one_time": True,
    "buttons": [
        [get_but('Записать настроение', 'positive'), get_but('Статистика', 'positive')],
    ]
}
main_menu = json.dumps(main_menu, ensure_ascii=False).encode('utf-8')
main_menu = str(main_menu.decode('utf-8'))

record_menu = {  # mood keyboard
    "one_time": True,
    "buttons": [
        [get_but('Счастье', 'positive'), get_but('Воодушевление', 'positive')],
        [get_but('Облегчение', 'positive'), get_but('Безразличие', 'positive')],
        [get_but('Тревожность', 'positive'), get_but('Апатия', 'positive')],
        [get_but('Раздражение', 'positive'), get_but('Печаль', 'positive')],
    ]
}
record_menu = json.dumps(record_menu, ensure_ascii=False).encode('utf-8')
record_menu = str(record_menu.decode('utf-8'))

ha = 0  # variable for each mood
ins = 0
re = 0
dis = 0
anx = 0
ap = 0
ir = 0
sad = 0


def record(id):  # informing about a successful record
    vkbot.method('messages.send', {'user_id': id, 'message': 'Записано!', 'random_id': 0, 'keyboard': main_menu})


def percent(res, sum):  # calculates the percentage for statistics
    return str(int(round((res / sum) * 100))) + '%'


def statistics(id):  # creates a dictionary with statistics and sends it to user
    cursor.execute(
        f"SELECT happiness, inspiration, relief, disinterest, anxiety, apathy, irritation, sadness from users WHERE id='{id}'")
    result = list(cursor)
    summary = sum(result[0])
    state = {'Счастье - ': percent(result[0][0], summary),
             'Воодушевление - ': percent(result[0][1], summary),
             'Облегчение - ': percent(result[0][2], summary),
             'Безразличие - ': percent(result[0][3], summary),
             'Тревожность - ': percent(result[0][4], summary),
             'Апатия - ': percent(result[0][5], summary),
             'Раздражение - ': percent(result[0][6], summary),
             'Печаль - ': percent(result[0][7], summary)}
    text = '\n'.join('{}{}'.format(key, val) for key, val in state.items())
    vkbot.method('messages.send', {'user_id': id, 'message': text, 'random_id': 0, 'keyboard': main_menu})


def send_welcome(id, text):  # sends greeting
    vkbot.method('messages.send', {'user_id': id, 'message': text, 'random_id': 0, 'keyboard': main_menu})


def send_record(id, text):  # brings out a mood keyboard
    vkbot.method('messages.send', {'user_id': id, 'message': text, 'random_id': 0, 'keyboard': record_menu})


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:

            msg = event.text.lower()
            id = event.user_id

            if msg == 'привет':
                send_welcome(id, 'Привет, какой у тебя красивый ID!')
                cursor.execute(
                    f"SELECT id from users WHERE id = '{id}'")  # creating a line in db for user if there is not such yet
                if cursor.fetchone() is None:
                    cursor.execute(f"INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                   (id, 0, 0, 0, 0, 0, 0, 0, 0))
                    db.commit()
            if msg == 'записать настроение':
                send_record(id, 'Что ты чувствуешь?')
            if msg == 'счастье':
                [ha], = cursor.execute(
                    f"SELECT happiness from users WHERE id = '{id}'")  # saving a value from db in valuable
                cursor.execute("""UPDATE users SET happiness = ? WHERE id = ?""", (ha + 1, id))  # updating database
                db.commit()
                record(id)
            if msg == 'воодушевление':
                [ins], = cursor.execute(f"SELECT inspiration from users WHERE id = '{id}'")
                cursor.execute("""UPDATE users SET inspiration = ? WHERE id = ?""", (ins + 1, id))
                db.commit()
                record(id)
            if msg == 'облегчение':
                [re], = cursor.execute(f"SELECT relief from users WHERE id = '{id}'")
                cursor.execute("""UPDATE users SET relief = ? WHERE id = ?""", (re + 1, id))
                db.commit()
                record(id)
            if msg == 'безразличие':
                [dis], = cursor.execute(f"SELECT disinterest from users WHERE id = '{id}'")
                cursor.execute("""UPDATE users SET disinterest = ? WHERE id = ?""", (dis + 1, id))
                db.commit()
                record(id)
            if msg == 'тревожность':
                [anx], = cursor.execute(f"SELECT anxiety from users WHERE id = '{id}'")
                cursor.execute("""UPDATE users SET anxiety = ? WHERE id = ?""", (anx + 1, id))
                db.commit()
                record(id)
            if msg == 'апатия':
                [ap], = cursor.execute(f"SELECT apathy from users WHERE id = '{id}'")
                cursor.execute("""UPDATE users SET apathy = ? WHERE id = ?""", (ap + 1, id))
                db.commit()
                record(id)
            if msg == 'раздражение':
                [ir], = cursor.execute(f"SELECT irritation from users WHERE id = '{id}'")
                cursor.execute("""UPDATE users SET irritation = ? WHERE id = ?""", (ir + 1, id))
                db.commit()
                record(id)
            if msg == 'печаль':
                [sad], = cursor.execute(f"SELECT sadness from users WHERE id = '{id}'")
                cursor.execute("""UPDATE users SET sadness = ? WHERE id = ?""", (sad + 1, id))
                db.commit()
                record(id)
            if msg == 'статистика':
                statistics(id)
