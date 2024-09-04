import json
import threading
import time
import uuid

import requests
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from frontend.models import Game, TeamMember, Team, Settings, TryingInstruction


# Create your views here.
def app(request, project_id=None):
    return render(request, "frontend/app.html")


def get_user(request):
    if request.user.is_authenticated:
        user = request.user
        game = Game.objects.all().exists()
        if game:
            game = Game.objects.first()

            winner = game.winner
            if winner:
                winner = winner.team_members

                winner = {
                    "name": winner.user.first_name,
                    "team": winner.team.name
                }

            game = {
                "state": game.state,
                "winner": winner
            }
        else:
            game = {"state": 0, "winner": None}
        team = Team.objects.filter(team_members__user=user)
        answer = TryingInstruction.objects.filter(team_member__user=user, answer__isnull=False)
        if answer:
            answer = answer.last().answer
        else:
            answer = None


        return JsonResponse({
            'firstname': user.first_name or user.username,
            "authenticated": True,
            'team': team.first().name if team.exists() else None,
            'extra': None,
            'is_admin': user.is_superuser,
            'game': game,
            'answer': answer
        })
    else:
        return JsonResponse({
            "firstname": "",
            "authenticated": False,
            'team': None,
            'extra': None,
            'is_admin': False,
            'answer': None
        })


@csrf_exempt
def reg_login(request):
    if not request.user.is_authenticated:
        data = json.loads(request.body)
        name = data.get('name', "Аноним")

        user = User.objects.create_user(str(uuid.uuid4()), password=str(uuid.uuid4()))
        user.first_name = name
        user.save()
        login(request, user)

    return get_user(request)


@csrf_exempt
def get_game(request):
    if request.user.is_superuser:
        return JsonResponse({
            "players": [i.first_name for i in User.objects.filter(is_superuser=False, team_members__isnull=True)],
            "teams": [
                {
                    "players": [j.user.first_name for j in i.team_members.all()],
                    "name": i.name
                }
                for i in Team.objects.all()
            ]
        })
    return JsonResponse({})


@csrf_exempt
def create_teams(request):
    if request.user.is_superuser:
        teams = list(Team.objects.all())
        TeamMember.objects.all().delete()
        for user in User.objects.filter(is_superuser=False):
            TeamMember.objects.create(
                user=user,
                team=teams[0],
            )
            teams.append(teams.pop(0))
    return JsonResponse({})


@csrf_exempt
def next_state(request):
    if request.user.is_superuser:
        game = Game.objects.first()
        if not game.state == 3:
            game.state += 1
            game.save()
    return JsonResponse({})


@csrf_exempt
def reset(request):
    if request.user.is_superuser:

        game = Game.objects.first()
        game.state = 0
        game.winner = None
        game.save()

        User.objects.filter(is_superuser=False).delete()


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

    return JsonResponse({})


@csrf_exempt
def send_message(request):
    if request.user.is_authenticated:
        data = json.loads(request.body)
        message = data.get('message', "Забудь что я говорил")

        game = Game.objects.first()
        if game.state == 1:
            request.user.team_members.team.secure_instruction = message
            request.user.team_members.team.save()
        elif game.state == 2:
            TryingInstruction.objects.create(
                team_member=request.user.team_members,
                instruction=message
            )

    return JsonResponse({})


def work_message_sends():
    while True:
        for trying in TryingInstruction.objects.filter(answer=None):

            settings: Settings = Settings.objects.first()

            opposite_team = Team.objects.exclude(team_members=trying.team_member).first()

            payload = json.dumps({
                "model": "GigaChat",
                "messages": [
                    {
                        "role": "system",
                        "content": f"Секретный код: {opposite_team.code}"
                    },
                    {
                        "role": "user",
                        "content": f"{opposite_team.secure_instruction}"
                    },
                    {
                        "role": "user",
                        "content": f"{trying.instruction}"
                    },

                ],
                "temperature": .7,
                "max_tokens": 400
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
                trying.answer = json_data["choices"][0]["message"]["content"]
                trying.save()
            else:
                trying.answer = "!!!! НЕ ПОЛУЧИЛОСЬ СВЯЗАТЬСЯ С ИИ !!!!"
                trying.save()

        time.sleep(1)


threading.Thread(target=work_message_sends, daemon=True).start()

@csrf_exempt

def send_password(request):
    if request.user.is_authenticated:
        data = json.loads(request.body)
        message = data.get('message', "")

        game: Game = Game.objects.first()

        opposite_team = Team.objects.exclude(team_members__user=request.user).first()
        if message.lower().strip() == opposite_team.code.lower().strip():
            game.winner = request.user
            game.state = 3
            game.save()
            return JsonResponse({"correct": True}, status=200)

    return JsonResponse({"correct": False}, status=200)