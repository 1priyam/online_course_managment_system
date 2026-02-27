# frontend/views.py
from django.shortcuts import render

def index(request):
    return render(request, 'login.html')

def serve_page(request, page):
    return render(request, f'{page}.html')