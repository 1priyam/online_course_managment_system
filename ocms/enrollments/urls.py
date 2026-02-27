# enrollments/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('enroll/', views.EnrollCourseView.as_view(), name='enroll-course'),
    path('my-courses/', views.MyCoursesView.as_view(), name='my-courses'),
    path('my-progress/', views.MyProgressView.as_view(), name='my-progress'),
    path('course/<int:course_id>/progress/', views.CourseProgressView.as_view(), name='course-progress'),
    path('lecture/<int:lecture_id>/complete/', views.MarkLectureCompleteView.as_view(), name='mark-complete'),
]