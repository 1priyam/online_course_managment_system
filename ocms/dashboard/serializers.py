# dashboard/serializers.py
from rest_framework import serializers

class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for admin dashboard statistics"""
    total_students = serializers.IntegerField()
    total_instructors = serializers.IntegerField()
    total_courses = serializers.IntegerField()
    total_enrollments = serializers.IntegerField()
    total_reviews = serializers.IntegerField()
    average_rating = serializers.FloatField()
    
class TopCourseSerializer(serializers.Serializer):
    """Serializer for top enrolled courses"""
    course_id = serializers.IntegerField()
    course_title = serializers.CharField()
    instructor_name = serializers.CharField()
    enrollment_count = serializers.IntegerField()
    average_rating = serializers.FloatField()
    
class RecentActivitySerializer(serializers.Serializer):
    """Serializer for recent platform activities"""
    type = serializers.CharField()  # 'enrollment', 'review', 'course'
    description = serializers.CharField()
    user_name = serializers.CharField()
    timestamp = serializers.DateTimeField()