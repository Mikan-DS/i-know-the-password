from django.contrib import admin

from .models import Settings


# Register your models here.
class SettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not Settings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Settings, SettingsAdmin)
