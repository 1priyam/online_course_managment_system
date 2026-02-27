# courses/serializers.py
from rest_framework import serializers
from .models import Category, Course, Module, Lecture
from accounts.serializers import UserProfileSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'created_at']
        read_only_fields = ['id', 'created_at']

class LectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecture
        fields = ['id', 'title', 'video_url', 'notes', 'order', 'duration']
        read_only_fields = ['id']

class ModuleSerializer(serializers.ModelSerializer):
    lectures = LectureSerializer(many=True, read_only=True)
    
    class Meta:
        model = Module
        fields = ['id', 'title', 'order', 'lectures']
        read_only_fields = ['id']

class CourseListSerializer(serializers.ModelSerializer):
    instructor_name = serializers.CharField(source='instructor.full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    total_modules = serializers.SerializerMethodField()
    total_lectures = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'price', 'level', 
            'instructor_name', 'category_name', 'is_published',
            'total_modules', 'total_lectures', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_modules(self, obj):
        return obj.modules.count()
    
    def get_total_lectures(self, obj):
        total = 0
        for module in obj.modules.all():
            total += module.lectures.count()
        return total

class CourseDetailSerializer(serializers.ModelSerializer):
    instructor = UserProfileSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    modules = ModuleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'price', 'level',
            'instructor', 'category', 'modules', 'is_published',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class CourseCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'title', 'description', 'price', 'level', 
            'category', 'is_published'
        ]
    
    def create(self, validated_data):
        # Automatically set instructor to current user
        validated_data['instructor'] = self.context['request'].user
        return super().create(validated_data)

class ModuleCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['title', 'order']

class LectureCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecture
        fields = ['title', 'video_url', 'notes', 'order', 'duration']