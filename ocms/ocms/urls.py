"""
URL configuration for ocms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/', include('courses.urls')),
    path('api/', include('enrollments.urls')),
    path('api/', include('reviews.urls')),
    path('api/', include('dashboard.urls')),
    
    # Frontend routes
    path('', TemplateView.as_view(template_name='login.html'), name='home'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('register/', TemplateView.as_view(template_name='register.html'), name='register'),
    path('student-dashboard/', TemplateView.as_view(template_name='student-dashboard.html'), name='student-dashboard'),
    path('courses/', TemplateView.as_view(template_name='courses.html'), name='courses'),
    path('my-courses/', TemplateView.as_view(template_name='my-courses.html'), name='my-courses'),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])