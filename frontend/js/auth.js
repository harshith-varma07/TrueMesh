/**
 * TrueMesh - Authentication JavaScript
 * Handles login, registration, and JWT token management
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';

// Toggle password visibility
function togglePassword() {
    const passwordInput = document.getElementById('password');
    const toggleBtn = document.querySelector('.toggle-password i');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleBtn.classList.remove('fa-eye');
        toggleBtn.classList.add('fa-eye-slash');
    } else {
        passwordInput.type = 'password';
        toggleBtn.classList.remove('fa-eye-slash');
        toggleBtn.classList.add('fa-eye');
    }
}

// Show toast notification
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Store authentication token
function storeAuthToken(token) {
    localStorage.setItem('truemesh_token', token);
    localStorage.setItem('truemesh_token_time', new Date().getTime());
}

// Get authentication token
function getAuthToken() {
    return localStorage.getItem('truemesh_token');
}

// Check if user is authenticated
function isAuthenticated() {
    const token = getAuthToken();
    const tokenTime = localStorage.getItem('truemesh_token_time');
    
    if (!token || !tokenTime) return false;
    
    // Check if token is older than 24 hours
    const hoursSinceLogin = (new Date().getTime() - parseInt(tokenTime)) / (1000 * 60 * 60);
    if (hoursSinceLogin > 24) {
        logout();
        return false;
    }
    
    return true;
}

// Store user data
function storeUserData(userData) {
    localStorage.setItem('truemesh_user', JSON.stringify(userData));
}

// Get user data
function getUserData() {
    const userData = localStorage.getItem('truemesh_user');
    return userData ? JSON.parse(userData) : null;
}

// Logout
function logout() {
    localStorage.removeItem('truemesh_token');
    localStorage.removeItem('truemesh_token_time');
    localStorage.removeItem('truemesh_user');
    window.location.href = 'login.html';
}

// Login form handler
document.getElementById('loginForm')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const remember = document.getElementById('remember').checked;
    const submitBtn = this.querySelector('button[type="submit"]');
    
    // Show loading state
    const originalHTML = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>Signing In...</span>';
    submitBtn.disabled = true;
    
    try {
        // Try API authentication first
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });
        
        if (response.ok) {
            const data = await response.json();
            storeAuthToken(data.access_token);
            storeUserData(data.user);
            showToast('Login successful! Redirecting...', 'success');
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1000);
        } else {
            throw new Error('Invalid credentials');
        }
    } catch (error) {
        console.log('API not available, using demo authentication');
        
        // Demo authentication (fallback when API is not running)
        const demoUsers = {
            'admin@truemesh.io': { password: 'Admin@123', role: 'admin', name: 'Admin User' },
            'reviewer@truemesh.io': { password: 'Review@123', role: 'reviewer', name: 'Reviewer User' }
        };
        
        const user = demoUsers[email];
        
        if (user && user.password === password) {
            // Generate demo token
            const demoToken = btoa(JSON.stringify({ email, role: user.role, timestamp: new Date().getTime() }));
            storeAuthToken(demoToken);
            storeUserData({ email, role: user.role, name: user.name });
            
            showToast('Login successful! Redirecting...', 'success');
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1000);
        } else {
            showToast('Invalid email or password', 'error');
            submitBtn.innerHTML = originalHTML;
            submitBtn.disabled = false;
        }
    }
});

// Check authentication on protected pages
function checkAuth() {
    const currentPage = window.location.pathname.split('/').pop();
    const publicPages = ['login.html', 'register.html', 'index.html', 'about.html'];
    
    if (!publicPages.includes(currentPage) && !isAuthenticated()) {
        window.location.href = 'login.html';
    }
}

// Add auth header to API requests
async function apiRequest(endpoint, options = {}) {
    const token = getAuthToken();
    const headers = {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers
        });
        
        if (response.status === 401) {
            logout();
            throw new Error('Unauthorized');
        }
        
        return response;
    } catch (error) {
        console.error('API Request failed:', error);
        throw error;
    }
}

// Auto-logout on token expiration
setInterval(() => {
    if (!isAuthenticated() && window.location.pathname !== '/login.html') {
        showToast('Session expired. Please login again.', 'warning');
        setTimeout(logout, 2000);
    }
}, 60000); // Check every minute

// Check auth on page load
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    
    // Display user info if logged in
    const userData = getUserData();
    if (userData) {
        document.querySelectorAll('.user-name').forEach(el => {
            el.textContent = userData.name || userData.email;
        });
        document.querySelectorAll('.user-email').forEach(el => {
            el.textContent = userData.email;
        });
        document.querySelectorAll('.user-role').forEach(el => {
            el.textContent = userData.role || 'User';
        });
    }
});

// Export functions for use in other scripts
window.TrueMeshAuth = {
    storeAuthToken,
    getAuthToken,
    isAuthenticated,
    storeUserData,
    getUserData,
    logout,
    showToast,
    apiRequest,
    API_BASE_URL
};
