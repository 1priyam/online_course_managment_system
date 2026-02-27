# courses/views.py
from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from .models import Category, Course, Module, Lecture
from .serializers import (
    CategorySerializer, CourseListSerializer, CourseDetailSerializer,
    CourseCreateUpdateSerializer, ModuleCreateUpdateSerializer,
    LectureCreateUpdateSerializer
)
from accounts.permissions import IsInstructor, IsAdminOrReadOnly


def safe_cache_get(key):
    try:
        return cache.get(key)
    except Exception:
        return None


def safe_cache_set(key, value, timeout=300):
    try:
        cache.set(key, value, timeout=timeout)
    except Exception:
        pass


def safe_cache_delete(key):
    try:
        cache.delete(key)
    except Exception:
        pass

# Category Views
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    
    def perform_create(self, serializer):
        # Only instructors and admins can create categories
        if self.request.user.role in ['INSTRUCTOR', 'ADMIN']:
            serializer.save()
        else:
            self.permission_denied(self.request)

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]

# Course Views
class CourseListView(generics.ListAPIView):
    """Public course listing - cached"""
    serializer_class = CourseListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['level', 'category', 'price']
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at', 'title']
    
    def get_queryset(self):
        # Try to get from cache first
        cache_key = 'published_courses'
        queryset = safe_cache_get(cache_key)
        
        if not queryset:
            queryset = Course.objects.filter(is_published=True).select_related('instructor', 'category').prefetch_related('modules__lectures')
            safe_cache_set(cache_key, queryset, timeout=300)  # Cache for 5 minutes
        
        return queryset

class CourseDetailView(generics.RetrieveAPIView):
    """Public course detail"""
    queryset = Course.objects.filter(is_published=True).select_related('instructor', 'category').prefetch_related('modules__lectures')
    serializer_class = CourseDetailSerializer
    permission_classes = [permissions.AllowAny]

class InstructorCourseListView(generics.ListCreateAPIView):
    """Instructor's courses"""
    permission_classes = [permissions.IsAuthenticated, IsInstructor]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CourseCreateUpdateSerializer
        return CourseListSerializer
    
    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user).select_related('category')
    
    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)

class InstructorCourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Instructor's course detail for editing"""
    permission_classes = [permissions.IsAuthenticated, IsInstructor]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CourseCreateUpdateSerializer
        return CourseDetailSerializer
    
    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user)
    
    def perform_update(self, serializer):
        # Clear cache when course is updated
        safe_cache_delete('published_courses')
        serializer.save()
    
    def perform_destroy(self, instance):
        # Clear cache when course is deleted
        safe_cache_delete('published_courses')
        instance.delete()

# Module Views
class ModuleListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsInstructor]
    serializer_class = ModuleCreateUpdateSerializer
    
    def get_queryset(self):
        course_id = self.kwargs['course_id']
        return Module.objects.filter(course_id=course_id, course__instructor=self.request.user)
    
    def perform_create(self, serializer):
        course_id = self.kwargs['course_id']
        course = Course.objects.get(id=course_id, instructor=self.request.user)
        serializer.save(course=course)
        # Clear cache
        safe_cache_delete('published_courses')

class ModuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsInstructor]
    serializer_class = ModuleCreateUpdateSerializer
    
    def get_queryset(self):
        return Module.objects.filter(course__instructor=self.request.user)
    
    def perform_update(self, serializer):
        safe_cache_delete('published_courses')
        serializer.save()
    
    def perform_destroy(self, instance):
        safe_cache_delete('published_courses')
        instance.delete()

# Lecture Views
class LectureListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsInstructor]
    serializer_class = LectureCreateUpdateSerializer
    
    def get_queryset(self):
        module_id = self.kwargs['module_id']
        return Lecture.objects.filter(
            module_id=module_id, 
            module__course__instructor=self.request.user
        )
    
    def perform_create(self, serializer):
        module_id = self.kwargs['module_id']
        module = Module.objects.get(id=module_id, course__instructor=self.request.user)
        serializer.save(module=module)
        safe_cache_delete('published_courses')

class LectureDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsInstructor]
    serializer_class = LectureCreateUpdateSerializer
    
    def get_queryset(self):
        return Lecture.objects.filter(module__course__instructor=self.request.user)
    
    def perform_update(self, serializer):
        safe_cache_delete('published_courses')
        serializer.save()
    
    def perform_destroy(self, instance):
        safe_cache_delete('published_courses')
        instance.delete()
