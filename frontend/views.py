import json
import uuid

import requests
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from frontend.models import Game, TeamMember, Team, Settings


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

                winner = winner.team_members.objects.first()

                winner = {
                    "name": winner.user.first_name,
                    "team": winner.team.name
                }

            game = {
                "state": game.state,
                "winner": winner
            }
        return JsonResponse({
            'firstname': user.first_name or user.username,
            "authenticated": True,
            'team': None,
            'extra': None,
            'is_admin': user.is_superuser,
            'game': game
        })
    else:
        return JsonResponse({
            "firstname": "",
            "authenticated": False,
            'team': None,
            'extra': None,
            'is_admin': False
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

def next_state(request):
    if request.user.is_superuser:
        game = Game.objects.first()
        if not game.state == 3:
            game.state += 1
            game.save()
    return JsonResponse({})


def reset(request):
    if request.user.is_superuser:

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
            settings.gigachat_expires_in = json_data['expires_at']


    return JsonResponse({})