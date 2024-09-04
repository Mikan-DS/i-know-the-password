from django.urls import path

from . import views

urlpatterns = [
    path('', views.app, name='app'),
    path('get-user/', views.get_user, name='get-user'),
    path('login/', views.reg_login, name='login'),
]
