from django.contrib import admin
from .models import SiteSetting, GalleryImage


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'updated_at']
    readonly_fields = ['updated_at']


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'order', 'is_active', 'created_at']
    list_filter = ['is_active']
    ordering = ['order']
