from django.contrib import admin

from .models import Story

@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = [
        "title", 
        "author", 
        "status", 
        "created_at", 
        "updated_at" 
        ]
    search_fields = [
        "title", 
        "content"
        ]
    list_filter = [
        "status", 
        "created_at"
        ]
    prepopulated_fields = {
        "slug": ("title",),
    }