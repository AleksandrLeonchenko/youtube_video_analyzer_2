from django.contrib import admin
from .models import UserFiles


class UserFilesAdmin(admin.ModelAdmin):
    list_display: list[str] = [
        'id',
        'user_id',
        'user_ip',
        'video_id',
        'cookie_value',
        'file_path',
    ]
    list_display_links: list[str] = list_display
    search_fields: list[str] = ['id']
    ordering: list[str] = ['id']


admin.site.register(UserFiles, UserFilesAdmin)

admin.site.site_title = 'Админ-панель приложения video_analyzer'
admin.site.site_header = 'Админ-панель приложения video_analyzer'
