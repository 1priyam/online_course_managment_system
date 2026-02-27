# reviews/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from django.core.cache import cache

from .models import Review
from courses.models import Course
from enrollments.models import Enrollment
from .serializers import ReviewSerializer, CreateReviewSerializer, CourseReviewSerializer

class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'STUDENT'

class CourseReviewListView(generics.ListAPIView):
    """Public API to get all reviews for a course"""
    serializer_class = CourseReviewSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return Review.objects.filter(course_id=course_id).select_related('student')

class CreateCourseReviewView(APIView):
    """API for students to create a review for a course they're enrolled in"""
    permission_classes = [permissions.IsAuthenticated, IsStudent]
    
    def post(self, request, course_id):
        # Check if course exists
        course = get_object_or_404(Course, id=course_id, is_published=True)
        
        # Check if student is enrolled in the course
        if not Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response(
                {"error": "You must be enrolled in this course to review it"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if student already reviewed this course
        if Review.objects.filter(student=request.user, course=course).exists():
            return Response(
                {"error": "You have already reviewed this course"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create review
        serializer = CreateReviewSerializer(data=request.data)
        if serializer.is_valid():
            review = Review.objects.create(
                student=request.user,
                course=course,
                rating=serializer.validated_data['rating'],
                comment=serializer.validated_data.get('comment', '')
            )
            
            # Clear cache for course reviews
            cache.delete(f'course_reviews_{course_id}')
            cache.delete(f'course_rating_{course_id}')
            
            return Response(
                CourseReviewSerializer(review).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateDeleteReviewView(APIView):
    """API for students to update or delete their own reviews"""
    permission_classes = [permissions.IsAuthenticated, IsStudent]
    
    def get_object(self, review_id, user):
        return get_object_or_404(Review, id=review_id, student=user)
    
    def put(self, request, review_id):
        review = self.get_object(review_id, request.user)
        
        serializer = CreateReviewSerializer(data=request.data)
        if serializer.is_valid():
            review.rating = serializer.validated_data['rating']
            review.comment = serializer.validated_data.get('comment', '')
            review.save()
            
            # Clear cache
            cache.delete(f'course_reviews_{review.course_id}')
            cache.delete(f'course_rating_{review.course_id}')
            
            return Response(CourseReviewSerializer(review).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, review_id):
        review = self.get_object(review_id, request.user)
        course_id = review.course_id
        review.delete()
        
        # Clear cache
        cache.delete(f'course_reviews_{course_id}')
        cache.delete(f'course_rating_{course_id}')
        
        return Response(
            {"message": "Review deleted successfully"},
            status=status.HTTP_200_OK
        )

class MyReviewsView(generics.ListAPIView):
    """API for students to see all their reviews"""
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]
    
    def get_queryset(self):
        return Review.objects.filter(student=self.request.user).select_related('course')

class CourseAverageRatingView(APIView):
    """Public API to get average rating for a course"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, course_id):
        # Try to get from cache
        cache_key = f'course_rating_{course_id}'
        rating_data = cache.get(cache_key)
        
        if not rating_data:
            course = get_object_or_404(Course, id=course_id)
            
            # Calculate average rating
            avg_rating = Review.objects.filter(course=course).aggregate(
                average=Avg('rating'),
                total=Count('id')
            )
            
            rating_data = {
                'course_id': course_id,
                'course_title': course.title,
                'average_rating': round(avg_rating['average'] or 0, 2),
                'total_reviews': avg_rating['total'] or 0
            }
            
            # Cache for 15 minutes
            cache.set(cache_key, rating_data, timeout=900)
        
        return Response(rating_data)