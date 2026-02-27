# reviews/admin.py
from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'course', 'rating', 'created_at')
    list_display_links = ('id', 'student')
    list_filter = ('rating', 'created_at')
    search_fields = ('student__email', 'student__full_name', 'course__title', 'comment')
    raw_id_fields = ('student', 'course')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('student', 'course', 'rating', 'comment')
        }),
    )