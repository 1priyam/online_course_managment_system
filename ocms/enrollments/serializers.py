# enrollments/serializers.py
from rest_framework import serializers
from .models import Enrollment, LectureProgress
from courses.models import Course, Lecture
from courses.serializers import CourseListSerializer

class EnrollmentSerializer(serializers.ModelSerializer):
    course_details = CourseListSerializer(source='course', read_only=True)
    
    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'course_details', 'status', 'enrolled_at']
        read_only_fields = ['id', 'enrolled_at']

class EnrollCourseSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    
    def validate_course_id(self, value):
        try:
            course = Course.objects.get(id=value, is_published=True)
        except Course.DoesNotExist:
            raise serializers.ValidationError("Course not found or not published")
        
        # Check if already enrolled
        user = self.context['request'].user
        if Enrollment.objects.filter(student=user, course=course).exists():
            raise serializers.ValidationError("Already enrolled in this course")
        
        return value

class LectureProgressSerializer(serializers.ModelSerializer):
    lecture_title = serializers.CharField(source='lecture.title', read_only=True)
    
    class Meta:
        model = LectureProgress
        fields = ['id', 'lecture', 'lecture_title', 'completed', 'completed_at']

class CourseProgressSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    course_title = serializers.CharField()
    total_lectures = serializers.IntegerField()
    completed_lectures = serializers.IntegerField()
    progress_percentage = serializers.FloatField()
    status = serializers.CharField()