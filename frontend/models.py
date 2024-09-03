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

    gigachat_access_token = models.CharField(max_length=500, blank=True, null=True, verbose_name="НЕ МЕНЯТЬ")
    gigachat_expired_at = models.IntegerField(default=0, verbose_name="НЕ МЕНЯТЬ")

    class Meta:
        verbose_name = "Настройка"
        verbose_name_plural = "Настройки"

    def __str__(self):
        return "Настройка"

    def save(self, *args, **kwargs):
        if not self.pk and Settings.objects.exists():
            raise ValueError('Настройка уникальна, больше создавать нельзя!')

        return super(Settings, self).save(*args, **kwargs)