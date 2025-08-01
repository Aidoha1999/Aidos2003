import requests
import time

TOKEN = '001.3277213606.1546113568:1011921225'
BASE_URL = 'https://myteam.mail.ru/bot/v1'

users_state = {}

CITIES = ['РђСЃС‚Р°РЅР°', 'РђР»РјР°С‚С‹', 'РЁС‹РјРєРµРЅС‚']
LECTORS = ['РўСѓСЂРјР°РЅРѕРІР° Р”.Рђ.', 'РЎРµРєСѓРѕРІР° РЁ.Р‘.']

LINKS = {
    'РљР°С‚Р°Р»РѕРі Р·Р°Р»РѕРІ': 'https://delicate-klepon-16140e.netlify.app/',
    'РљРѕРЅСЃСѓР»СЊС‚Р°С†РёСЏ': 'https://example.com/consultation',
    'РЇРІРєР° РЅР° СЃРµРјРёРЅР°СЂ': 'https://comforting-torrone-5273b1.netlify.app/'
}

OPTIONS = list(LINKS.keys()) + ['Р¤РёРЅР°РЅСЃРѕРІС‹Р№ РѕС‚С‡РµС‚']

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
    send_buttons(chat_id, "рџ‘‹ Р”РѕР±СЂРѕ РїРѕР¶Р°Р»РѕРІР°С‚СЊ! РЇ Р±РѕС‚ РєРѕРјРїР°РЅРёРё Astana Orleu.\nР’С‹Р±РµСЂРёС‚Рµ РЅСѓР¶РЅС‹Р№ СЂР°Р·РґРµР»:", OPTIONS, "option")
    users_state[chat_id] = {'step': 'choose_option'}

def start_report(chat_id):
    users_state[chat_id] = {'step': 'choose_city', 'data': {}}
    send_buttons(chat_id, "Р’С‹Р±РµСЂРёС‚Рµ РіРѕСЂРѕРґ:", CITIES, "city")

def process_message(chat_id, text):
    state = users_state.get(chat_id)

    if text.startswith("option:"):
        selected = text.split("option:", 1)[1]
        if selected == 'Р¤РёРЅР°РЅСЃРѕРІС‹Р№ РѕС‚С‡РµС‚':
            start_report(chat_id)
        else:
            send_message(chat_id, f"Р’РѕС‚ РІР°С€Р° СЃСЃС‹Р»РєР°: {LINKS[selected]}")
            users_state.pop(chat_id, None)

    elif text.startswith("city:"):
        city = text.split("city:", 1)[1]
        state['data']['city'] = city
        state['step'] = 'choose_lector'
        send_buttons(chat_id, f"Р’С‹Р±СЂР°РЅ РіРѕСЂРѕРґ: {city}\nР’С‹Р±РµСЂРёС‚Рµ Р»РµРєС‚РѕСЂР°:", LECTORS, "lector")

    elif text.startswith("lector:"):
        lector = text.split("lector:", 1)[1]
        state['data']['lector'] = lector
        state['step'] = 'enter_date'
        send_message(chat_id, f"Р’С‹Р±СЂР°РЅ Р»РµРєС‚РѕСЂ: {lector}\nР’РІРµРґРёС‚Рµ РґР°С‚Сѓ СЃРµРјРёРЅР°СЂР° (РЅР°РїСЂРёРјРµСЂ, 30 РјР°СЏ):")

    elif state and state['step'] == 'enter_date':
        state['data']['date'] = text.strip()
        state['step'] = 'enter_start_sum'
        send_message(chat_id, "Р’РІРµРґРёС‚Рµ СЃСѓРјРјСѓ РЅР° РЅР°С‡Р°Р»Рѕ РґРЅСЏ (С‚Рі):")

    elif state and state['step'] == 'enter_start_sum':
        if text.isdigit():
            state['data']['start_sum'] = int(text)
            state['data']['expenses'] = []
            state['step'] = 'enter_expense'
            send_message(chat_id, "Р’РІРµРґРёС‚Рµ Р·Р°С‚СЂР°С‚С‹ РІ С„РѕСЂРјР°С‚Рµ:\nРћРїРёСЃР°РЅРёРµ: СЃСѓРјРјР°\nРќР°РїСЂРёРјРµСЂ:\nРўР°РєСЃРё РґРѕ Р·Р°Р»Р°: 960\n\nР”Р»СЏ Р·Р°РІРµСЂС€РµРЅРёСЏ РІРІРµРґРёС‚Рµ СЃР»РѕРІРѕ 'РіРѕС‚РѕРІРѕ'")
        else:
            send_message(chat_id, "Р’РІРµРґРёС‚Рµ СЃСѓРјРјСѓ С‡РёСЃР»РѕРј Р±РµР· РїСЂРѕР±РµР»РѕРІ.")

    elif state and state['step'] == 'enter_expense':
        data = state['data']
        if text.lower() == 'РіРѕС‚РѕРІРѕ':
            total = sum(x[1] for x in data['expenses'])
            remainder = data['start_sum'] - total
            lines = [
                f"Рі. {data['city']}",
                f"Р›РµРєС‚РѕСЂ: {data['lector']}",
                f"{data['date']}\n",
                f"РЎСѓРјРјР° РЅР° РЅР°С‡Р°Р»Рѕ РґРЅСЏ: {data['start_sum']} С‚Рі\n",
                "Р—Р°С‚СЂР°С‚С‹:"
            ] + [f"{desc}: {amt} С‚Рі" for desc, amt in data['expenses']] + [
                f"\nРС‚РѕРіРѕ СЂР°СЃС…РѕРґС‹: {total} С‚Рі",
                f"РЎСѓРјРјР° РѕСЃС‚Р°С‚РєР°: {remainder} С‚Рі"
            ]
            send_message(chat_id, '\n'.join(lines))
            users_state.pop(chat_id, None)
        else:
            if ':' in text:
                desc, amt_str = text.split(':', 1)
                amt_str = amt_str.strip().replace('С‚Рі', '').strip()
                if amt_str.isdigit():
                    data['expenses'].append((desc.strip(), int(amt_str)))
                    send_message(chat_id, f"Р”РѕР±Р°РІР»РµРЅРѕ: {desc.strip()} вЂ” {amt_str} С‚Рі\nР’РІРµРґРёС‚Рµ СЃР»РµРґСѓСЋС‰СѓСЋ РёР»Рё 'РіРѕС‚РѕРІРѕ'")
                else:
                    send_message(chat_id, "РЎСѓРјРјР° РґРѕР»Р¶РЅР° Р±С‹С‚СЊ С‡РёСЃР»РѕРј. РџРѕРїСЂРѕР±СѓР№С‚Рµ СЃРЅРѕРІР°.")
            else:
                send_message(chat_id, "РќРµРІРµСЂРЅС‹Р№ С„РѕСЂРјР°С‚. РСЃРїРѕР»СЊР·СѓР№С‚Рµ 'РћРїРёСЃР°РЅРёРµ: СЃСѓРјРјР°'.")

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
    print("рџ¤– Р‘РѕС‚ Р·Р°РїСѓС‰РµРЅ. РћР¶РёРґР°РЅРёРµ СЃРѕР±С‹С‚РёР№...")
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
                        print(f"вћЎпёЏ РљРЅРѕРїРєР°: {callback}")
                        process_message(chat_id, callback)
                    elif message:
                        print(f"рџ’¬ РЎРѕРѕР±С‰РµРЅРёРµ: {message}")
                        process_message(chat_id, message)
        else:
            time.sleep(1)

if __name__ == '__main__':
    main()