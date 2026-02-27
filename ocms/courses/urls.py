# courses/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Public course endpoints
    path('courses/', views.CourseListView.as_view(), name='course-list'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('categories/', views.CategoryListCreateView.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
    
    # Instructor endpoints
    path('instructor/courses/', views.InstructorCourseListView.as_view(), name='instructor-courses'),
    path('instructor/courses/<int:pk>/', views.InstructorCourseDetailView.as_view(), name='instructor-course-detail'),
    
    # Module endpoints
    path('instructor/courses/<int:course_id>/modules/', views.ModuleListCreateView.as_view(), name='module-list'),
    path('instructor/modules/<int:pk>/', views.ModuleDetailView.as_view(), name='module-detail'),
    
    # Lecture endpoints
    path('instructor/modules/<int:module_id>/lectures/', views.LectureListCreateView.as_view(), name='lecture-list'),
    path('instructor/lectures/<int:pk>/', views.LectureDetailView.as_view(), name='lecture-detail'),
]