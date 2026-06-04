from django.contrib import admin
from .models import SiteSetting, GalleryImage, StoredImage


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'updated_at']
    readonly_fields = ['updated_at']


@admin.register(StoredImage)
class StoredImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'filename', 'content_type', 'size', 'created_at']
    readonly_fields = ['id', 'size', 'created_at']


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'caption', 'order', 'is_active', 'created_at']
    list_display_links = ['id', 'caption']
    list_filter = ['is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['caption']
    ordering = ['order', '-created_at']
    actions = ['hard_delete_selected']

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="/api/images/{obj.image.id}/" style="max-height:80px; border-radius:6px;" />'
        return '-'
    image_preview.allow_tags = True
    image_preview.short_description = 'Preview'

    def hard_delete_selected(self, request, queryset):
        count = queryset.count()
        for obj in queryset:
            if obj.image:
                obj.image.delete()
        queryset.delete()
        self.message_user(request, f'{count} gallery image(s) hard deleted.')
    hard_delete_selected.short_description = 'Hard delete selected images (removes from DB)'
