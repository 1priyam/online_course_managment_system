# dashboard/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.core.cache import cache
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta

from accounts.models import User
from courses.models import Course
from enrollments.models import Enrollment
from reviews.models import Review
from .serializers import DashboardStatsSerializer, TopCourseSerializer, RecentActivitySerializer

class IsAdminUser(permissions.BasePermission):
    """Custom permission to only allow admins"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADMIN'

class AdminDashboardStatsView(APIView):
    """
    API endpoint for admin dashboard statistics
    Cached in Redis for 5 minutes
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Try to get from cache first
        cache_key = 'admin_dashboard_stats'
        stats = cache.get(cache_key)
        
        if not stats:
            # Calculate statistics
            total_students = User.objects.filter(role='STUDENT').count()
            total_instructors = User.objects.filter(role='INSTRUCTOR').count()
            total_courses = Course.objects.filter(is_published=True).count()
            total_enrollments = Enrollment.objects.count()
            total_reviews = Review.objects.count()
            
            # Calculate average rating
            avg_rating = Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0
            
            stats = {
                'total_students': total_students,
                'total_instructors': total_instructors,
                'total_courses': total_courses,
                'total_enrollments': total_enrollments,
                'total_reviews': total_reviews,
                'average_rating': round(avg_rating, 2)
            }
            
            # Cache for 5 minutes
            cache.set(cache_key, stats, timeout=300)
        
        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data)

class AdminTopCoursesView(APIView):
    """
    API endpoint for top enrolled courses
    Cached in Redis for 5 minutes
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Try to get from cache
        cache_key = 'admin_top_courses'
        top_courses = cache.get(cache_key)
        
        if not top_courses:
            # Get courses with most enrollments
            courses = Course.objects.filter(is_published=True).annotate(
                enrollment_count=Count('enrollments'),
                avg_rating=Avg('reviews__rating')
            ).order_by('-enrollment_count')[:10]
            
            top_courses = []
            for course in courses:
                top_courses.append({
                    'course_id': course.id,
                    'course_title': course.title,
                    'instructor_name': course.instructor.full_name,
                    'enrollment_count': course.enrollment_count,
                    'average_rating': round(course.avg_rating or 0, 2)
                })
            
            # Cache for 5 minutes
            cache.set(cache_key, top_courses, timeout=300)
        
        serializer = TopCourseSerializer(top_courses, many=True)
        return Response(serializer.data)

class AdminRecentActivityView(APIView):
    """
    API endpoint for recent platform activities
    Not cached - shows real-time data
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        recent_activities = []
        
        # Get recent enrollments (last 7 days)
        recent_enrollments = Enrollment.objects.select_related('student', 'course').order_by('-enrolled_at')[:5]
        for enrollment in recent_enrollments:
            recent_activities.append({
                'type': 'enrollment',
                'description': f"Enrolled in {enrollment.course.title}",
                'user_name': enrollment.student.full_name,
                'timestamp': enrollment.enrolled_at
            })
        
        # Get recent reviews (last 7 days)
        recent_reviews = Review.objects.select_related('student', 'course').order_by('-created_at')[:5]
        for review in recent_reviews:
            recent_activities.append({
                'type': 'review',
                'description': f"Reviewed {review.course.title} - {review.rating}★",
                'user_name': review.student.full_name,
                'timestamp': review.created_at
            })
        
        # Get recent courses (last 7 days)
        recent_courses = Course.objects.filter(is_published=True).select_related('instructor').order_by('-created_at')[:5]
        for course in recent_courses:
            recent_activities.append({
                'type': 'course',
                'description': f"New course: {course.title}",
                'user_name': course.instructor.full_name,
                'timestamp': course.created_at
            })
        
        # Sort by timestamp (most recent first) and take top 10
        recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
        recent_activities = recent_activities[:10]
        
        serializer = RecentActivitySerializer(recent_activities, many=True)
        return Response(serializer.data)

class InstructorDashboardStatsView(APIView):
    """
    API endpoint for instructor dashboard statistics
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if request.user.role != 'INSTRUCTOR':
            return Response(
                {"error": "Only instructors can access this"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get instructor's courses
        courses = Course.objects.filter(instructor=request.user)
        total_courses = courses.count()
        
        # Calculate total students across all courses
        total_students = Enrollment.objects.filter(course__in=courses).values('student').distinct().count()
        
        # Calculate total revenue
        total_revenue = sum(course.price for course in courses if course.price)
        
        # Get average rating for instructor's courses
        avg_rating = Review.objects.filter(course__in=courses).aggregate(avg=Avg('rating'))['avg'] or 0
        
        stats = {
            'total_courses': total_courses,
            'total_students': total_students,
            'total_revenue': float(total_revenue),
            'average_rating': round(avg_rating, 2),
            'recent_courses': [
                {
                    'id': course.id,
                    'title': course.title,
                    'enrollments': course.enrollments.count(),
                    'rating': round(Review.objects.filter(course=course).aggregate(avg=Avg('rating'))['avg'] or 0, 2)
                }
                for course in courses.order_by('-created_at')[:5]
            ]
        }
        
        return Response(stats)

class StudentDashboardStatsView(APIView):
    """
    API endpoint for student dashboard statistics
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if request.user.role != 'STUDENT':
            return Response(
                {"error": "Only students can access this"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get student's enrollments
        enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
        total_enrolled = enrollments.count()
        completed_courses = enrollments.filter(status='COMPLETED').count()
        
        # Calculate progress for each course
        courses_in_progress = []
        for enrollment in enrollments.filter(status='ACTIVE'):
            total_lectures = enrollment.course.modules.aggregate(
                total=models.Sum('lectures__duration')
            )['total'] or 0
            
            completed_lectures = enrollment.lecture_progress.filter(completed=True).count()
            progress = (completed_lectures / total_lectures * 100) if total_lectures > 0 else 0
            
            courses_in_progress.append({
                'course_id': enrollment.course.id,
                'course_title': enrollment.course.title,
                'instructor': enrollment.course.instructor.full_name,
                'progress': round(progress, 2),
                'enrolled_at': enrollment.enrolled_at
            })
        
        stats = {
            'total_enrolled': total_enrolled,
            'completed_courses': completed_courses,
            'in_progress': len(courses_in_progress),
            'courses': courses_in_progress[:5]  # Show last 5
        }
        
        return Response(stats)