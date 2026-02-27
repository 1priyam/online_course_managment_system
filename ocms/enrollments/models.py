# enrollments/models.py
from django.db import models
from django.conf import settings

class Enrollment(models.Model):
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
    )
    
    id = models.BigAutoField(primary_key=True)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.full_name} - {self.course.title}"
    
    class Meta:
        db_table = 'enrollments_enrollment'
        unique_together = ['student', 'course']  # Prevent duplicate enrollments

class LectureProgress(models.Model):
    id = models.BigAutoField(primary_key=True)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='lecture_progress')
    lecture = models.ForeignKey('courses.Lecture', on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.enrollment.student.full_name} - {self.lecture.title}"
    
    class Meta:
        db_table = 'enrollments_lectureprogress'
        unique_together = ['enrollment', 'lecture']