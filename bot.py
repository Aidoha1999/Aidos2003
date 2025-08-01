import requests
import time

TOKEN = '001.3277213606.1546113568:1011921225'
BASE_URL = 'https://myteam.mail.ru/bot/v1'

users_state = {}

CITIES = ['Р С’РЎРѓРЎвЂљР В°Р Р…Р В°', 'Р С’Р В»Р СР В°РЎвЂљРЎвЂ№', 'Р РЃРЎвЂ№Р СР С”Р ВµР Р…РЎвЂљ']
LECTORS = ['Р СћРЎС“РЎР‚Р СР В°Р Р…Р С•Р Р†Р В° Р вЂќ.Р С’.', 'Р РЋР ВµР С”РЎС“Р С•Р Р†Р В° Р РЃ.Р вЂ.']

LINKS = {
    'Р С™Р В°РЎвЂљР В°Р В»Р С•Р С– Р В·Р В°Р В»Р С•Р Р†': 'https://delicate-klepon-16140e.netlify.app/',
    'Р С™Р С•Р Р…РЎРѓРЎС“Р В»РЎРЉРЎвЂљР В°РЎвЂ Р С‘РЎРЏ': 'https://example.com/consultation',
    'Р Р‡Р Р†Р С”Р В° Р Р…Р В° РЎРѓР ВµР СР С‘Р Р…Р В°РЎР‚': 'https://comforting-torrone-5273b1.netlify.app/'
}

OPTIONS = list(LINKS.keys()) + ['Р В¤Р С‘Р Р…Р В°Р Р…РЎРѓР С•Р Р†РЎвЂ№Р в„– Р С•РЎвЂљРЎвЂЎР ВµРЎвЂљ']

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
    send_buttons(chat_id, "СЂСџвЂвЂ№ Р вЂќР С•Р В±РЎР‚Р С• Р С—Р С•Р В¶Р В°Р В»Р С•Р Р†Р В°РЎвЂљРЎРЉ! Р Р‡ Р В±Р С•РЎвЂљ Р С”Р С•Р СР С—Р В°Р Р…Р С‘Р С‘ Astana Orleu.\nР вЂ™РЎвЂ№Р В±Р ВµРЎР‚Р С‘РЎвЂљР Вµ Р Р…РЎС“Р В¶Р Р…РЎвЂ№Р в„– РЎР‚Р В°Р В·Р Т‘Р ВµР В»:", OPTIONS, "option")
    users_state[chat_id] = {'step': 'choose_option'}

def start_report(chat_id):
    users_state[chat_id] = {'step': 'choose_city', 'data': {}}
    send_buttons(chat_id, "Р вЂ™РЎвЂ№Р В±Р ВµРЎР‚Р С‘РЎвЂљР Вµ Р С–Р С•РЎР‚Р С•Р Т‘:", CITIES, "city")

def process_message(chat_id, text):
    state = users_state.get(chat_id)

    if text.startswith("option:"):
        selected = text.split("option:", 1)[1]
        if selected == 'Р В¤Р С‘Р Р…Р В°Р Р…РЎРѓР С•Р Р†РЎвЂ№Р в„– Р С•РЎвЂљРЎвЂЎР ВµРЎвЂљ':
            start_report(chat_id)
        else:
            send_message(chat_id, f"Р вЂ™Р С•РЎвЂљ Р Р†Р В°РЎв‚¬Р В° РЎРѓРЎРѓРЎвЂ№Р В»Р С”Р В°: {LINKS[selected]}")
            users_state.pop(chat_id, None)

    elif text.startswith("city:"):
        city = text.split("city:", 1)[1]
        state['data']['city'] = city
        state['step'] = 'choose_lector'
        send_buttons(chat_id, f"Р вЂ™РЎвЂ№Р В±РЎР‚Р В°Р Р… Р С–Р С•РЎР‚Р С•Р Т‘: {city}\nР вЂ™РЎвЂ№Р В±Р ВµРЎР‚Р С‘РЎвЂљР Вµ Р В»Р ВµР С”РЎвЂљР С•РЎР‚Р В°:", LECTORS, "lector")

    elif text.startswith("lector:"):
        lector = text.split("lector:", 1)[1]
        state['data']['lector'] = lector
        state['step'] = 'enter_date'
        send_message(chat_id, f"Р вЂ™РЎвЂ№Р В±РЎР‚Р В°Р Р… Р В»Р ВµР С”РЎвЂљР С•РЎР‚: {lector}\nР вЂ™Р Р†Р ВµР Т‘Р С‘РЎвЂљР Вµ Р Т‘Р В°РЎвЂљРЎС“ РЎРѓР ВµР СР С‘Р Р…Р В°РЎР‚Р В° (Р Р…Р В°Р С—РЎР‚Р С‘Р СР ВµРЎР‚, 30 Р СР В°РЎРЏ):")

    elif state and state['step'] == 'enter_date':
        state['data']['date'] = text.strip()
        state['step'] = 'enter_start_sum'
        send_message(chat_id, "Р вЂ™Р Р†Р ВµР Т‘Р С‘РЎвЂљР Вµ РЎРѓРЎС“Р СР СРЎС“ Р Р…Р В° Р Р…Р В°РЎвЂЎР В°Р В»Р С• Р Т‘Р Р…РЎРЏ (РЎвЂљР С–):")

    elif state and state['step'] == 'enter_start_sum':
        if text.isdigit():
            state['data']['start_sum'] = int(text)
            state['data']['expenses'] = []
            state['step'] = 'enter_expense'
            send_message(chat_id, "Р вЂ™Р Р†Р ВµР Т‘Р С‘РЎвЂљР Вµ Р В·Р В°РЎвЂљРЎР‚Р В°РЎвЂљРЎвЂ№ Р Р† РЎвЂћР С•РЎР‚Р СР В°РЎвЂљР Вµ:\nР С›Р С—Р С‘РЎРѓР В°Р Р…Р С‘Р Вµ: РЎРѓРЎС“Р СР СР В°\nР СњР В°Р С—РЎР‚Р С‘Р СР ВµРЎР‚:\nР СћР В°Р С”РЎРѓР С‘ Р Т‘Р С• Р В·Р В°Р В»Р В°: 960\n\nР вЂќР В»РЎРЏ Р В·Р В°Р Р†Р ВµРЎР‚РЎв‚¬Р ВµР Р…Р С‘РЎРЏ Р Р†Р Р†Р ВµР Т‘Р С‘РЎвЂљР Вµ РЎРѓР В»Р С•Р Р†Р С• 'Р С–Р С•РЎвЂљР С•Р Р†Р С•'")
        else:
            send_message(chat_id, "Р вЂ™Р Р†Р ВµР Т‘Р С‘РЎвЂљР Вµ РЎРѓРЎС“Р СР СРЎС“ РЎвЂЎР С‘РЎРѓР В»Р С•Р С Р В±Р ВµР В· Р С—РЎР‚Р С•Р В±Р ВµР В»Р С•Р Р†.")

    elif state and state['step'] == 'enter_expense':
        data = state['data']
        if text.lower() == 'Р С–Р С•РЎвЂљР С•Р Р†Р С•':
            total = sum(x[1] for x in data['expenses'])
            remainder = data['start_sum'] - total
            lines = [
                f"Р С–. {data['city']}",
                f"Р вЂєР ВµР С”РЎвЂљР С•РЎР‚: {data['lector']}",
                f"{data['date']}\n",
                f"Р РЋРЎС“Р СР СР В° Р Р…Р В° Р Р…Р В°РЎвЂЎР В°Р В»Р С• Р Т‘Р Р…РЎРЏ: {data['start_sum']} РЎвЂљР С–\n",
                "Р вЂ”Р В°РЎвЂљРЎР‚Р В°РЎвЂљРЎвЂ№:"
            ] + [f"{desc}: {amt} РЎвЂљР С–" for desc, amt in data['expenses']] + [
                f"\nР ВРЎвЂљР С•Р С–Р С• РЎР‚Р В°РЎРѓРЎвЂ¦Р С•Р Т‘РЎвЂ№: {total} РЎвЂљР С–",
                f"Р РЋРЎС“Р СР СР В° Р С•РЎРѓРЎвЂљР В°РЎвЂљР С”Р В°: {remainder} РЎвЂљР С–"
            ]
            send_message(chat_id, '\n'.join(lines))
            users_state.pop(chat_id, None)
        else:
            if ':' in text:
                desc, amt_str = text.split(':', 1)
                amt_str = amt_str.strip().replace('РЎвЂљР С–', '').strip()
                if amt_str.isdigit():
                    data['expenses'].append((desc.strip(), int(amt_str)))
                    send_message(chat_id, f"Р вЂќР С•Р В±Р В°Р Р†Р В»Р ВµР Р…Р С•: {desc.strip()} РІР‚вЂќ {amt_str} РЎвЂљР С–\nР вЂ™Р Р†Р ВµР Т‘Р С‘РЎвЂљР Вµ РЎРѓР В»Р ВµР Т‘РЎС“РЎР‹РЎвЂ°РЎС“РЎР‹ Р С‘Р В»Р С‘ 'Р С–Р С•РЎвЂљР С•Р Р†Р С•'")
                else:
                    send_message(chat_id, "Р РЋРЎС“Р СР СР В° Р Т‘Р С•Р В»Р В¶Р Р…Р В° Р В±РЎвЂ№РЎвЂљРЎРЉ РЎвЂЎР С‘РЎРѓР В»Р С•Р С. Р СџР С•Р С—РЎР‚Р С•Р В±РЎС“Р в„–РЎвЂљР Вµ РЎРѓР Р…Р С•Р Р†Р В°.")
            else:
                send_message(chat_id, "Р СњР ВµР Р†Р ВµРЎР‚Р Р…РЎвЂ№Р в„– РЎвЂћР С•РЎР‚Р СР В°РЎвЂљ. Р ВРЎРѓР С—Р С•Р В»РЎРЉР В·РЎС“Р в„–РЎвЂљР Вµ 'Р С›Р С—Р С‘РЎРѓР В°Р Р…Р С‘Р Вµ: РЎРѓРЎС“Р СР СР В°'.")

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
    print("СЂСџВ¤вЂ“ Р вЂР С•РЎвЂљ Р В·Р В°Р С—РЎС“РЎвЂ°Р ВµР Р…. Р С›Р В¶Р С‘Р Т‘Р В°Р Р…Р С‘Р Вµ РЎРѓР С•Р В±РЎвЂ№РЎвЂљР С‘Р в„–...")
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
                        print(f"РІС›РЋРїС‘РЏ Р С™Р Р…Р С•Р С—Р С”Р В°: {callback}")
                        process_message(chat_id, callback)
                    elif message:
                        print(f"СЂСџвЂ™В¬ Р РЋР С•Р С•Р В±РЎвЂ°Р ВµР Р…Р С‘Р Вµ: {message}")
                        process_message(chat_id, message)
        else:
            time.sleep(1)

if __name__ == '__main__':
    main()