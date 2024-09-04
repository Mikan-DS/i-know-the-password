from django.urls import path

from . import views

urlpatterns = [
    path('', views.app, name='app'),
    path('get-user/', views.get_user, name='get-user'),
    path('login/', views.reg_login, name='login'),
    path('update/', views.get_game, name='get-game'),
    path('create-teams/', views.create_teams, name='create_teams'),
    path('next/', views.next_state, name='next'),
    path('reset/', views.reset, name='reset'),
    path('send-message/', views.send_message, name='send-message'),
]
