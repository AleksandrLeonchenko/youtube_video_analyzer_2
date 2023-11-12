from django.contrib import admin
from .models import ProcessedFiles, SourceVideoFiles


class ProcessedFilesAdmin(admin.ModelAdmin):
    list_display: list[str] = [
        'id',
        'file_name',
        'file_path',
        'date_of_creation'
    ]
    list_display_links: list[str] = list_display
    search_fields: list[str] = ['id']
    ordering: list[str] = ['id']


class SourceVideoFilesAdmin(admin.ModelAdmin):
    list_display: list[str] = [
        'id',
        # 'file_name',
        'video_file',
        'date_of_download',
        'processed'
    ]
    list_display_links: list[str] = list_display
    search_fields: list[str] = ['id']
    ordering: list[str] = ['id']


admin.site.register(ProcessedFiles, ProcessedFilesAdmin)
admin.site.register(SourceVideoFiles, SourceVideoFilesAdmin)

admin.site.site_title = 'Админ-панель приложения object_detection'
admin.site.site_header = 'Админ-панель приложения object_detection'
