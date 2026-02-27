# reviews/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Public endpoints
    path('courses/<int:course_id>/reviews/', views.CourseReviewListView.as_view(), name='course-reviews'),
    path('courses/<int:course_id>/rating/', views.CourseAverageRatingView.as_view(), name='course-rating'),
    
    # Student endpoints
    path('courses/<int:course_id>/reviews/create/', views.CreateCourseReviewView.as_view(), name='create-review'),
    path('reviews/my/', views.MyReviewsView.as_view(), name='my-reviews'),
    path('reviews/<int:review_id>/', views.UpdateDeleteReviewView.as_view(), name='review-detail'),
]