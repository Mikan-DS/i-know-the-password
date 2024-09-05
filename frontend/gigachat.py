import datetime
import json
import typing
import uuid
from fp.fp import FreeProxy

import requests

from .models import Settings

class GigaChatMessage:
    def __init__(self, message, role="user"):
        self.message = message
        self.role = role


def gigachat_request(url, headers, payload, is_second_try=False):
    settings: Settings = Settings.objects.first()

    proxies = None
    if settings.gigachat_use_proxy:
        if not settings.gigachat_last_working_proxy:
            settings.gigachat_last_working_proxy = FreeProxy(country_id=['RU'], https=True).get()
            settings.save()
        proxies = {
            "https": settings.gigachat_last_working_proxy
        }

    try:
        return requests.request(
            "POST",
            url,
            headers=headers,
            data=payload,
            verify=settings.russian_cert.path,
            proxies=proxies
        )
    except Exception as e:
        if settings.gigachat_use_proxy and not is_second_try:
            settings.gigachat_last_working_proxy = FreeProxy(country_id=['RU'], https=True).get()
            settings.save()
            gigachat_request(url, headers, payload, True)
        else:
            raise e

def update_token():
    settings: Settings = Settings.objects.first()

    payload = f'scope={settings.SCOPES[settings.gigachat_scope][1]}'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'RqUID': str(uuid.uuid4()),
        'Accept': 'application/json',
        'Authorization': f'Basic {settings.gigachat_auth_data}'
    }

    response = gigachat_request(
        settings.gigachat_auth_url,
        headers,
        payload
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
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {settings.gigachat_access_token}'
    }

    response = gigachat_request(
        "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
        headers,
        payload
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
