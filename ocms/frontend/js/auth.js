// frontend/js/auth.js

const IS_LOCAL_STATIC = window.location.port === '5500' || window.location.protocol === 'file:';
const APP_ORIGIN = IS_LOCAL_STATIC ? 'http://127.0.0.1:8000' : '';
const API_BASE = `${APP_ORIGIN}/api`;

function apiUrl(path) {
    const normalized = path.startsWith('/') ? path : `/${path}`;
    return `${API_BASE}${normalized}`;
}

function appPath(path) {
    const normalized = path.startsWith('/') ? path : `/${path}`;
    return `${APP_ORIGIN}${normalized}`;
}

window.apiUrl = apiUrl;
window.appPath = appPath;

function isAuthenticated() {
    return !!localStorage.getItem('access_token');
}

function getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
}

function getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    return {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };
}

async function handleResponse(response) {
    if (response.status === 401) {
        const refreshed = await refreshToken();
        if (!refreshed) {
            logout();
        }
    }
    return response;
}

async function refreshToken() {
    const refresh = localStorage.getItem('refresh_token');
    if (!refresh) return false;

    try {
        const response = await fetch(apiUrl('/auth/refresh/'), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ refresh })
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access);
            return true;
        }
    } catch (error) {
        console.error('Token refresh failed:', error);
    }

    logout();
    return false;
}

function logout() {
    localStorage.clear();
    window.location.href = appPath('/login/');
}

function redirectBasedOnRole() {
    const user = getCurrentUser();
    if (!user) {
        window.location.href = appPath('/login/');
        return;
    }

    const currentPath = window.location.pathname;

    if (user.role === 'STUDENT' && !currentPath.includes('student')) {
        window.location.href = appPath('/student-dashboard/');
    } else if (user.role === 'INSTRUCTOR' || user.role === 'ADMIN') {
        window.location.href = appPath('/courses/');
    }
}

function showError(message, elementId = 'error-message') {
    const errorDiv = document.getElementById(elementId);
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        errorDiv.className = 'alert alert-error';

        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    } else {
        alert(message);
    }
}

function showSuccess(message, elementId = 'error-message') {
    const successDiv = document.getElementById(elementId);
    if (successDiv) {
        successDiv.textContent = message;
        successDiv.style.display = 'block';
        successDiv.className = 'alert alert-success';

        setTimeout(() => {
            successDiv.style.display = 'none';
        }, 3000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const currentPath = window.location.pathname.toLowerCase();
    const isPublicPage = currentPath === '/' ||
        currentPath === '/login/' ||
        currentPath === '/register/' ||
        currentPath.endsWith('/login.html') ||
        currentPath.endsWith('/register.html');

    if (!isPublicPage && !isAuthenticated()) {
        window.location.href = appPath('/login/');
    }
});