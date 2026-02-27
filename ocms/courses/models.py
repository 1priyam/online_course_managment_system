# courses/models.py
from django.db import models
from django.conf import settings

class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'courses_category'
        indexes = [
            models.Index(fields=['slug']),
        ]

class Course(models.Model):
    LEVEL_CHOICES = (
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    )
    
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='Beginner')
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses_taught')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'courses_course'
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['price']),
            models.Index(fields=['level']),
            models.Index(fields=['instructor']),
        ]

class Module(models.Model):
    id = models.BigAutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    order = models.IntegerField()
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    class Meta:
        db_table = 'courses_module'
        unique_together = ['course', 'order']
        ordering = ['order']

class Lecture(models.Model):
    id = models.BigAutoField(primary_key=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lectures')
    title = models.CharField(max_length=200)
    video_url = models.URLField(max_length=500, blank=True)
    notes = models.TextField(blank=True)
    order = models.IntegerField()
    duration = models.IntegerField(help_text="Duration in seconds", default=0)
    
    def __str__(self):
        return f"{self.module.title} - {self.title}"
    
    class Meta:
        db_table = 'courses_lecture'
        unique_together = ['module', 'order']
        ordering = ['order']