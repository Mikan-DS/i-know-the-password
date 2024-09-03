from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import Settings


@receiver(post_migrate)
def create_default_settings(sender, **kwargs):
    if not Settings.objects.exists():
        Settings.objects.create()
