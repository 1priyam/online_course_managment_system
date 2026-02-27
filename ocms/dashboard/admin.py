# dashboard/admin.py
from django.contrib import admin
from django.core.cache import cache
from django.shortcuts import render
from django.urls import path
from django.db.models import Count, Avg
from accounts.models import User
from courses.models import Course
from enrollments.models import Enrollment
from reviews.models import Review

class DashboardAdmin(admin.AdminSite):
    site_header = 'OCMS Administration'
    site_title = 'OCMS Admin'
    index_title = 'Online Course Management System'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='dashboard'),
        ]
        return custom_urls + urls
    
    def dashboard_view(self, request):
        # Get statistics
        total_students = User.objects.filter(role='STUDENT').count()
        total_instructors = User.objects.filter(role='INSTRUCTOR').count()
        total_courses = Course.objects.count()
        total_enrollments = Enrollment.objects.count()
        total_reviews = Review.objects.count()
        
        # Get recent activities
        recent_enrollments = Enrollment.objects.select_related('student', 'course').order_by('-enrolled_at')[:5]
        recent_reviews = Review.objects.select_related('student', 'course').order_by('-created_at')[:5]
        
        context = {
            'total_students': total_students,
            'total_instructors': total_instructors,
            'total_courses': total_courses,
            'total_enrollments': total_enrollments,
            'total_reviews': total_reviews,
            'recent_enrollments': recent_enrollments,
            'recent_reviews': recent_reviews,
        }
        return render(request, 'admin/dashboard.html', context)

# Create a custom admin site
admin_site = DashboardAdmin(name='myadmin')