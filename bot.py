import requests
import time

TOKEN = '001.3277213606.1546113568:1011921225'
BASE_URL = 'https://myteam.mail.ru/bot/v1'

users_state = {}

CITIES = ['������', '������', '�������']
LECTORS = ['��������� �.�.', '������� �.�.']

LINKS = {
    '������� �����': 'https://delicate-klepon-16140e.netlify.app/',
    '������������': 'https://example.com/consultation',
    '���� �� �������': 'https://comforting-torrone-5273b1.netlify.app/'
}

OPTIONS = list(LINKS.keys()) + ['���������� �����']

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
    send_buttons(chat_id, "?? ����� ����������! � ��� �������� Astana Orleu.\n�������� ������ ������:", OPTIONS, "option")
    users_state[chat_id] = {'step': 'choose_option'}

def start_report(chat_id):
    users_state[chat_id] = {'step': 'choose_city', 'data': {}}
    send_buttons(chat_id, "�������� �����:", CITIES, "city")

def process_message(chat_id, text):
    state = users_state.get(chat_id)

    if text.startswith("option:"):
        selected = text.split("option:", 1)[1]
        if selected == '���������� �����':
            start_report(chat_id)
        else:
            send_message(chat_id, f"��� ���� ������: {LINKS[selected]}")
            users_state.pop(chat_id, None)

    elif text.startswith("city:"):
        city = text.split("city:", 1)[1]
        state['data']['city'] = city
        state['step'] = 'choose_lector'
        send_buttons(chat_id, f"������ �����: {city}\n�������� �������:", LECTORS, "lector")

    elif text.startswith("lector:"):
        lector = text.split("lector:", 1)[1]
        state['data']['lector'] = lector
        state['step'] = 'enter_date'
        send_message(chat_id, f"������ ������: {lector}\n������� ���� �������� (��������, 30 ���):")

    elif state and state['step'] == 'enter_date':
        state['data']['date'] = text.strip()
        state['step'] = 'enter_start_sum'
        send_message(chat_id, "������� ����� �� ������ ��� (��):")

    elif state and state['step'] == 'enter_start_sum':
        if text.isdigit():
            state['data']['start_sum'] = int(text)
            state['data']['expenses'] = []
            state['step'] = 'enter_expense'
            send_message(chat_id, "������� ������� � �������:\n��������: �����\n��������:\n����� �� ����: 960\n\n��� ���������� ������� ����� '������'")
        else:
            send_message(chat_id, "������� ����� ������ ��� ��������.")

    elif state and state['step'] == 'enter_expense':
        data = state['data']
        if text.lower() == '������':
            total = sum(x[1] for x in data['expenses'])
            remainder = data['start_sum'] - total
            lines = [
                f"�. {data['city']}",
                f"������: {data['lector']}",
                f"{data['date']}\n",
                f"����� �� ������ ���: {data['start_sum']} ��\n",
                "�������:"
            ] + [f"{desc}: {amt} ��" for desc, amt in data['expenses']] + [
                f"\n����� �������: {total} ��",
                f"����� �������: {remainder} ��"
            ]
            send_message(chat_id, '\n'.join(lines))
            users_state.pop(chat_id, None)
        else:
            if ':' in text:
                desc, amt_str = text.split(':', 1)
                amt_str = amt_str.strip().replace('��', '').strip()
                if amt_str.isdigit():
                    data['expenses'].append((desc.strip(), int(amt_str)))
                    send_message(chat_id, f"���������: {desc.strip()} � {amt_str} ��\n������� ��������� ��� '������'")
                else:
                    send_message(chat_id, "����� ������ ���� ������. ���������� �����.")
            else:
                send_message(chat_id, "�������� ������. ����������� '��������: �����'.")

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
    print("? ��� �������. �������� �������...")
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
                        print(f"?? ������: {callback}")
                        process_message(chat_id, callback)
                    elif message:
                        print(f"?? ���������: {message}")
                        process_message(chat_id, message)
        else:
            time.sleep(1)

if __name__ == '__main__':
    main()