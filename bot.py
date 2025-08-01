import requests
import time

TOKEN = '001.3277213606.1546113568:1011921225'
BASE_URL = 'https://myteam.mail.ru/bot/v1'

users_state = {}

CITIES = ['Астана', 'Алматы', 'Шымкент']
LECTORS = ['Турманова Д.А.', 'Секуова Ш.Б.']

LINKS = {
    'Каталог залов': 'https://delicate-klepon-16140e.netlify.app/',
    'Консультация': 'https://example.com/consultation',
    'Явка на семинар': 'https://comforting-torrone-5273b1.netlify.app/'
}

OPTIONS = list(LINKS.keys()) + ['Финансовый отчет']

def send_buttons(chat_id, text, buttons, prefix):
    url = f'{BASE_URL}/messages/sendInteractive'
    params = {'token': TOKEN}
    data = {
        'chatId': chat_id,
        'parts': [{
            'text': text,
            'buttons': [{'text': b, 'callbackData': f"{prefix}:{b}"} for b in buttons]
        }]
    }
    requests.post(url, params=params, json=data)

def send_message(chat_id, text):
    url = f'{BASE_URL}/messages/sendText'
    params = {'token': TOKEN}
    data = {'chatId': chat_id, 'text': text}
    requests.post(url, params=params, data=data)

def send_main_menu(chat_id):
    send_buttons(chat_id, "👋 Добро пожаловать! Я бот компании Astana Orleu.\nВыберите нужный раздел:", OPTIONS, "option")
    users_state[chat_id] = {'step': 'choose_option'}

def start_report(chat_id):
    users_state[chat_id] = {'step': 'choose_city', 'data': {}}
    send_buttons(chat_id, "Выберите город:", CITIES, "city")

def process_message(chat_id, text):
    state = users_state.get(chat_id)

    if text.startswith("option:"):
        selected = text.split("option:", 1)[1]
        if selected == 'Финансовый отчет':
            start_report(chat_id)
        else:
            send_message(chat_id, f"Вот ваша ссылка: {LINKS[selected]}")
            users_state.pop(chat_id, None)

    elif text.startswith("city:"):
        city = text.split("city:", 1)[1]
        state['data']['city'] = city
        state['step'] = 'choose_lector'
        send_buttons(chat_id, f"Выбран город: {city}\nВыберите лектора:", LECTORS, "lector")

    elif text.startswith("lector:"):
        lector = text.split("lector:", 1)[1]
        state['data']['lector'] = lector
        state['step'] = 'enter_date'
        send_message(chat_id, f"Выбран лектор: {lector}\nВведите дату семинара (например, 30 мая):")

    elif state and state['step'] == 'enter_date':
        state['data']['date'] = text.strip()
        state['step'] = 'enter_start_sum'
        send_message(chat_id, "Введите сумму на начало дня (тг):")

    elif state and state['step'] == 'enter_start_sum':
        if text.isdigit():
            state['data']['start_sum'] = int(text)
            state['data']['expenses'] = []
            state['step'] = 'enter_expense'
            send_message(chat_id, "Введите затраты в формате:\nОписание: сумма\nНапример:\nТакси до зала: 960\n\nДля завершения введите слово 'готово'")
        else:
            send_message(chat_id, "Введите сумму числом без пробелов.")

    elif state and state['step'] == 'enter_expense':
        data = state['data']
        if text.lower() == 'готово':
            total = sum(x[1] for x in data['expenses'])
            remainder = data['start_sum'] - total
            lines = [
                f"г. {data['city']}",
                f"Лектор: {data['lector']}",
                f"{data['date']}\n",
                f"Сумма на начало дня: {data['start_sum']} тг\n",
                "Затраты:"
            ] + [f"{desc}: {amt} тг" for desc, amt in data['expenses']] + [
                f"\nИтого расходы: {total} тг",
                f"Сумма остатка: {remainder} тг"
            ]
            send_message(chat_id, '\n'.join(lines))
            users_state.pop(chat_id, None)
        else:
            if ':' in text:
                desc, amt_str = text.split(':', 1)
                amt_str = amt_str.strip().replace('тг', '').strip()
                if amt_str.isdigit():
                    data['expenses'].append((desc.strip(), int(amt_str)))
                    send_message(chat_id, f"Добавлено: {desc.strip()} — {amt_str} тг\nВведите следующую или 'готово'")
                else:
                    send_message(chat_id, "Сумма должна быть числом. Попробуйте снова.")
            else:
                send_message(chat_id, "Неверный формат. Используйте 'Описание: сумма'.")

def get_updates(last_event_id):
    url = f'{BASE_URL}/events/get'
    params = {
        'token': TOKEN,
        'lastEventId': last_event_id,
        'pollTime': 25
    }
    response = requests.get(url, params=params, timeout=30)
    return response.json()

def main():
    print("🤖 Бот запущен. Ожидание событий...")
    last_event_id = 0
    while True:
        updates = get_updates(last_event_id)
        events = updates.get("events", [])
        if events:
            for event in events:
                last_event_id = event["eventId"]
                if event["type"] == "newMessage":
                    chat_id = event["payload"]["chat"]["chatId"]
                    message = event["payload"].get("text", "")
                    callback = event["payload"].get("callbackData")
                    if callback:
                        print(f"➡️ Кнопка: {callback}")
                        process_message(chat_id, callback)
                    elif message:
                        print(f"💬 Сообщение: {message}")
                        process_message(chat_id, message)
        else:
            time.sleep(1)

if __name__ == '__main__':
    main()