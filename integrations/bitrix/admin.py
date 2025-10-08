from django.contrib import admin

from . import models


@admin.register(models.Settings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        # Разрешаем создать только один объект
        settings_count = models.Settings.objects.count()
        return settings_count < 1
