from django.contrib import admin
from service.models import Chat


@admin.register(Chat)
class UserAdmin(admin.ModelAdmin):
    list_display = ('title', 'telegram_id', 'group_number', 'is_sender',)