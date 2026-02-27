# reviews/serializers.py
from rest_framework import serializers
from .models import Review
from accounts.serializers import UserProfileSerializer

class ReviewSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'student', 'student_name', 'course', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'student', 'created_at']

class CreateReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value

class CourseReviewSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'student_name', 'rating', 'comment', 'created_at']