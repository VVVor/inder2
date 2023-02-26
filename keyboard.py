import json

def get_button(text, color):
    return {
        "action": {
            "type": "text",
            "payload": "{\"button\": \"" + "1" + "\"}",
            "label": f"{text}"
        },
        "color": f"{color}"
    }


hallo_keyboard = {
    "one_time": True,
    "buttons": [
        [get_button('Привет!', 'primary')],
    ]
}
hallo_keyboard = json.dumps(hallo_keyboard, ensure_ascii=False).encode('utf-8')
hallo_keyboard = str(hallo_keyboard.decode('utf-8'))

sql_keyboard = {
    "one_time": True,
    "buttons": [
        [get_button('Познакомиться', 'primary')],
    ]
}
sql_keyboard = json.dumps(sql_keyboard, ensure_ascii=False).encode('utf-8')
sql_keyboard = str(sql_keyboard.decode('utf-8'))

next_keyboard = {
    "one_time": True,
    "buttons": [
        [get_button('Дальше', 'primary')],
    ]
}

next_keyboard = json.dumps(next_keyboard, ensure_ascii=False).encode('utf-8')
next_keyboard = str(next_keyboard.decode('utf-8'))

more_keyboard = {
    "one_time": True,
    "buttons": [
        [get_button('Загрузить еще', 'primary')],
    ]
}

more_keyboard = json.dumps(more_keyboard, ensure_ascii=False).encode('utf-8')
more_keyboard = str(more_keyboard.decode('utf-8'))