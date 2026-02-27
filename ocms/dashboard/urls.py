# dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Admin dashboard endpoints
    path('admin/analytics/', views.AdminDashboardStatsView.as_view(), name='admin-analytics'),
    path('admin/top-courses/', views.AdminTopCoursesView.as_view(), name='admin-top-courses'),
    path('admin/recent-activity/', views.AdminRecentActivityView.as_view(), name='admin-recent-activity'),
    
    # Instructor dashboard
    path('instructor/dashboard/', views.InstructorDashboardStatsView.as_view(), name='instructor-dashboard'),
    
    # Student dashboard
    path('student/dashboard/', views.StudentDashboardStatsView.as_view(), name='student-dashboard'),
]