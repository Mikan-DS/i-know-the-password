import datetime
import json
import typing
import uuid

import requests

from .models import Settings

class GigaChatMessage:
    def __init__(self, message, role="user"):
        self.message = message
        self.role = role

def update_token():
    settings: Settings = Settings.objects.first()

    payload = f'scope={settings.SCOPES[settings.gigachat_scope][1]}'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'RqUID': str(uuid.uuid4()),
        'Accept': 'application/json',
        'Authorization': f'Basic {settings.gigachat_auth_data}'
    }

    response = requests.request(
        "POST",
        settings.gigachat_auth_url,
        headers=headers,
        data=payload,
        verify=settings.russian_cert.path
    )

    if response.status_code == 200:
        json_data = response.json()
        settings.gigachat_access_token = json_data['access_token']
        settings.gigachat_expired_at = json_data['expires_at']
        settings.save()
    else:
        raise Exception(response.text)

def send_message(messages: typing.List[GigaChatMessage], temperature=.7, max_tokens=400, model="GigaChat"):
    settings: Settings = Settings.objects.first()

    gigachat_expired_at = int(str(settings.gigachat_expired_at)[:10])

    if datetime.datetime.utcfromtimestamp(gigachat_expired_at) < datetime.datetime.now():
        update_token()

    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": message.role, "content": message.message} for message in messages
            # {
            #     "role": "system",
            #     "content": f"Секретный код: {opposite_team.code}"
            # },
            # {
            #     "role": "user",
            #     "content": f"{opposite_team.secure_instruction}"
            # },
            # {
            #     "role": "user",
            #     "content": f"{trying.instruction}"
            # },

        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {settings.gigachat_access_token}'
    }

    response = requests.request(
        "POST",
        "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
        headers=headers,
        data=payload,
        verify=settings.russian_cert.path
    )

    if response.status_code == 200:
        json_data = response.json()
        return json_data["choices"][0]["message"]["content"]
        trying.answer = ""
        trying.save()
    else:
        print(response)
        return "!!!! НЕ ПОЛУЧИЛОСЬ СВЯЗАТЬСЯ С ИИ !!!!"
        trying.answer = "!!!! НЕ ПОЛУЧИЛОСЬ СВЯЗАТЬСЯ С ИИ !!!!"
        trying.save()
