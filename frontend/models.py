from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Settings(models.Model):
    gigachat_auth_data = models.CharField(max_length=500, blank=True, null=True, verbose_name="Базовая аутентификация")
    gigachat_auth_url = models.URLField(
        default='https://ngw.devices.sberbank.ru:9443/api/v2/oauth',
        verbose_name="Ссыллка для авторизации")

    SCOPES = [
        (0, "GIGACHAT_API_PERS")
    ]

    gigachat_scope = models.IntegerField(default=0, choices=SCOPES, verbose_name="Версия API")

    gigachat_access_token = models.CharField(max_length=1700, blank=True, null=True, verbose_name="НЕ МЕНЯТЬ")
    gigachat_expired_at = models.IntegerField(default=0, verbose_name="НЕ МЕНЯТЬ")

    russian_cert = models.FileField(upload_to='support_files/', verbose_name="Сертификат с госуслуг", blank=True, null=True)

    class Meta:
        verbose_name = "Настройка"
        verbose_name_plural = "Настройки"

    def __str__(self):
        return "Настройка"

    def save(self, *args, **kwargs):
        if not self.pk and Settings.objects.exists():
            raise ValueError('Настройка уникальна, больше создавать нельзя!')

        return super(Settings, self).save(*args, **kwargs)


class Game(models.Model):
    STATES = [
        (0, "Игра не началась"),
        (1, "Ввод инструкций для защиты"),
        (2, "Ввод инструкций для взлома"),
        (3, "Раунд завершен")
    ]

    state = models.IntegerField(choices=STATES, default=0, verbose_name="Стадия игры")

    winner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Победитель", null=True, blank=True)


class Team(models.Model):
    name = models.CharField(max_length=30, unique=True, verbose_name="Название команды")
    code = models.CharField(max_length=30, verbose_name="Секретный код")
    secure_instruction = models.TextField(max_length=400, verbose_name="Инструкции для защиты", null=True, blank=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, verbose_name="Игра")


class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, verbose_name="Команда", null=True, blank=True, related_name="team_members")
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Игрок", related_name="team_members")


class TryingInstruction(models.Model):
    team_member = models.ForeignKey(TeamMember, on_delete=models.CASCADE, verbose_name="Игрок")
    instruction = models.TextField(max_length=500, verbose_name="Инструкция")
    answer = models.TextField(max_length=1000, verbose_name="Ответ ИИ", null=True, blank=True)
