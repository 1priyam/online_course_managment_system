# Online Course Management System

A full-stack online course management platform built with Django REST Framework and a static HTML/CSS/JS frontend.

## Features

- User authentication and registration
- Course listing and course detail pages
- Student dashboard and enrolled courses pages
- REST API modules for:
  - `accounts`
  - `courses`
  - `enrollments`
  - `reviews`
  - `dashboard`

## Project Structure

- `ocms/` - Django backend project and apps
- `ocms/frontend/` - Static frontend pages, CSS, and JS
- `static/` - Shared static assets

## Tech Stack

- Python
- Django
- Django REST Framework
- HTML, CSS, JavaScript

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/1priyam/online_course_managment_system.git
cd online_course_managment_system
```

### 2. Create and activate virtual environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install django djangorestframework
```

### 4. Run migrations

```bash
cd ocms
python manage.py migrate
```

### 5. Start development server

```bash
python manage.py runserver
```

Open: `http://127.0.0.1:8000/`

## API Apps

- `accounts` - user model, serializers, authentication endpoints
- `courses` - course CRUD and related views
- `enrollments` - course enrollment management
- `reviews` - user reviews for courses
- `dashboard` - aggregated dashboard data

## Frontend Pages

Available under `ocms/frontend/pages/`:

- `login.html`
- `register.html`
- `courses.html`
- `courses-detail.html`
- `student-dashboard.html`
- `my-courses.html`

## Notes

- This repository currently tracks some `__pycache__` and `.pyc` files.
- Consider adding a `.gitignore` update in future cleanup.