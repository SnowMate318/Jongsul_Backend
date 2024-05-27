from django.contrib import admin
from .models import User, Shared

class userAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'email','is_staff', 'is_active','created_at')
    list_filter = ('is_staff', 'is_active', 'created_at')
    search_fields = ('username', 'email')
    ordering = ('-created_at',)
# Register your models here.
admin.site.register(User, userAdmin)

class SharedAdmin(admin.ModelAdmin):
    list_display = ('shared_title', 'user', 'shared_upload_datetime', 'is_activated', 'is_deleted', 'download_count')
    list_filter = ('is_activated', 'is_deleted', 'shared_upload_datetime')
    search_fields = ('shared_title', 'shared_content', 'user__username')
    ordering = ('is_deleted','-shared_upload_datetime',)
admin.site.register(Shared, SharedAdmin)
