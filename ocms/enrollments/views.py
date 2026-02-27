# enrollments/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Count, Sum

from .models import Enrollment, LectureProgress
from courses.models import Course, Lecture
from .serializers import EnrollmentSerializer, EnrollCourseSerializer, LectureProgressSerializer, CourseProgressSerializer

class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'STUDENT'

class EnrollCourseView(APIView):
    """API endpoint for students to enroll in a course"""
    permission_classes = [permissions.IsAuthenticated, IsStudent]
    
    def post(self, request):
        serializer = EnrollCourseSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            course_id = serializer.validated_data['course_id']
            course = Course.objects.get(id=course_id)
            
            # Create enrollment
            enrollment = Enrollment.objects.create(
                student=request.user,
                course=course,
                status='ACTIVE'
            )
            
            # Create lecture progress entries for all lectures in the course
            lectures = Lecture.objects.filter(module__course=course)
            for lecture in lectures:
                LectureProgress.objects.create(
                    enrollment=enrollment,
                    lecture=lecture,
                    completed=False
                )
            
            return Response({
                'message': 'Successfully enrolled in course',
                'enrollment_id': enrollment.id
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MyCoursesView(generics.ListAPIView):
    """API endpoint for students to see their enrolled courses"""
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]
    
    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user).select_related('course__instructor')

class CourseProgressView(APIView):
    """API endpoint to get progress for a specific course"""
    permission_classes = [permissions.IsAuthenticated, IsStudent]
    
    def get(self, request, course_id):
        # Get enrollment
        enrollment = get_object_or_404(Enrollment, student=request.user, course_id=course_id)
        
        # Get all lectures for the course
        total_lectures = Lecture.objects.filter(module__course_id=course_id).count()
        
        # Get completed lectures
        completed_lectures = LectureProgress.objects.filter(
            enrollment=enrollment,
            completed=True
        ).count()
        
        # Calculate progress
        progress_percentage = (completed_lectures / total_lectures * 100) if total_lectures > 0 else 0
        
        # Update enrollment status if all lectures completed
        if progress_percentage == 100 and enrollment.status == 'ACTIVE':
            enrollment.status = 'COMPLETED'
            enrollment.save()
        
        data = {
            'course_id': course_id,
            'course_title': enrollment.course.title,
            'total_lectures': total_lectures,
            'completed_lectures': completed_lectures,
            'progress_percentage': round(progress_percentage, 2),
            'status': enrollment.status
        }
        
        serializer = CourseProgressSerializer(data)
        return Response(serializer.data)

class MarkLectureCompleteView(APIView):
    """API endpoint to mark a lecture as completed"""
    permission_classes = [permissions.IsAuthenticated, IsStudent]
    
    def post(self, request, lecture_id):
        # Get lecture progress
        lecture_progress = get_object_or_404(
            LectureProgress,
            lecture_id=lecture_id,
            enrollment__student=request.user
        )
        
        # Mark as completed
        if not lecture_progress.completed:
            lecture_progress.completed = True
            lecture_progress.completed_at = timezone.now()
            lecture_progress.save()
            
            return Response({'message': 'Lecture marked as completed'})
        
        return Response({'message': 'Lecture already completed'})

class MyProgressView(APIView):
    """API endpoint to get progress for all enrolled courses"""
    permission_classes = [permissions.IsAuthenticated, IsStudent]
    
    def get(self, request):
        enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
        
        progress_data = []
        for enrollment in enrollments:
            total_lectures = Lecture.objects.filter(module__course=enrollment.course).count()
            completed_lectures = LectureProgress.objects.filter(
                enrollment=enrollment,
                completed=True
            ).count()
            
            progress = (completed_lectures / total_lectures * 100) if total_lectures > 0 else 0
            
            progress_data.append({
                'course_id': enrollment.course.id,
                'course_title': enrollment.course.title,
                'total_lectures': total_lectures,
                'completed_lectures': completed_lectures,
                'progress': round(progress, 2),
                'status': enrollment.status,
                'enrolled_at': enrollment.enrolled_at
            })
        
        return Response(progress_data)