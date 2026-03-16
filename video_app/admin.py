from django.contrib import admin
from django.utils.html import format_html

from .models import Video

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    readonly_fields = ('thumbnail_url', 'conversion_status')
    
    list_display = ('title', 'category', 'conversion_status')
