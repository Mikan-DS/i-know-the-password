import json
import uuid

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from frontend.models import Game, TeamMember


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

            ]
        })
    return JsonResponse({})