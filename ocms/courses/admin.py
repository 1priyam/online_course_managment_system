# courses/admin.py
from django.contrib import admin
from .models import Category, Course, Module, Lecture
from accounts.models import User

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'created_at')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('-created_at',)

class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1
    fields = ('title', 'order')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'instructor', 'category', 'price', 'level', 'is_published', 'created_at')
    list_display_links = ('id', 'title')
    list_filter = ('level', 'is_published', 'category')
    search_fields = ('title', 'description')
    list_editable = ('is_published',)
    inlines = [ModuleInline]
    autocomplete_fields = ('instructor', 'category')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'instructor')
        }),
        ('Classification', {
            'fields': ('category', 'level', 'price')
        }),
        ('Status', {
            'fields': ('is_published',)
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'instructor':
            kwargs['queryset'] = User.objects.filter(
                role__in=['INSTRUCTOR', 'ADMIN'],
                is_active=True
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class LectureInline(admin.TabularInline):
    model = Lecture
    extra = 1
    fields = ('title', 'order', 'duration', 'video_url')

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'course', 'order')
    list_display_links = ('id', 'title')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')
    inlines = [LectureInline]
    ordering = ('course', 'order')

@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'module', 'order', 'duration')
    list_display_links = ('id', 'title')
    list_filter = ('module__course',)
    search_fields = ('title', 'notes')
    ordering = ('module', 'order')
