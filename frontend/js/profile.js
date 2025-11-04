/**
 * TrueMesh - Profile Page JavaScript
 */

// Toggle password visibility for specific field
function togglePasswordField(fieldId) {
    const field = document.getElementById(fieldId);
    const button = field.parentElement.querySelector('.toggle-password i');
    
    if (field.type === 'password') {
        field.type = 'text';
        button.classList.remove('fa-eye');
        button.classList.add('fa-eye-slash');
    } else {
        field.type = 'password';
        button.classList.remove('fa-eye-slash');
        button.classList.add('fa-eye');
    }
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        window.TrueMeshAuth.showToast('Copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy:', err);
        window.TrueMeshAuth.showToast('Failed to copy', 'error');
    });
}

// Toggle API key visibility
let apiKeyVisible = false;
const actualApiKey = 'truemesh_api_key_' + Math.random().toString(36).substring(2, 15);

function toggleApiKey() {
    const apiKeyElement = document.getElementById('apiKey');
    const button = apiKeyElement.parentElement.querySelector('.btn-copy i');
    
    if (apiKeyVisible) {
        apiKeyElement.textContent = '••••••••••••••••••••••••••••••••';
        button.classList.remove('fa-eye-slash');
        button.classList.add('fa-eye');
    } else {
        apiKeyElement.textContent = actualApiKey;
        button.classList.remove('fa-eye');
        button.classList.add('fa-eye-slash');
    }
    
    apiKeyVisible = !apiKeyVisible;
}

// Regenerate API key
function regenerateApiKey() {
    if (confirm('Are you sure you want to regenerate your API key? Your current key will be invalidated.')) {
        // Show loading
        window.TrueMeshAuth.showToast('Regenerating API key...', 'warning');
        
        // Simulate API call
        setTimeout(() => {
            const newKey = 'truemesh_api_key_' + Math.random().toString(36).substring(2, 15);
            document.getElementById('apiKey').textContent = newKey;
            apiKeyVisible = true;
            window.TrueMeshAuth.showToast('API key regenerated successfully!', 'success');
        }, 1500);
    }
}

// Enable 2FA
function enable2FA() {
    window.TrueMeshAuth.showToast('Two-factor authentication setup coming soon', 'warning');
}

// Toggle sidebar
function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('collapsed');
}

// Profile form submission
document.getElementById('profileForm')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const submitBtn = this.querySelector('button[type="submit"]');
    const originalHTML = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
    submitBtn.disabled = true;
    
    // Get form data
    const fullName = document.getElementById('fullName').value;
    const phone = document.getElementById('phone').value;
    const organization = document.getElementById('organization').value;
    
    try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Update stored user data
        const userData = window.TrueMeshAuth.getUserData();
        userData.name = fullName;
        userData.phone = phone;
        userData.organization = organization;
        window.TrueMeshAuth.storeUserData(userData);
        
        // Update display
        document.querySelectorAll('.user-name').forEach(el => {
            el.textContent = fullName || userData.email;
        });
        
        window.TrueMeshAuth.showToast('Profile updated successfully!', 'success');
    } catch (error) {
        window.TrueMeshAuth.showToast('Failed to update profile', 'error');
    } finally {
        submitBtn.innerHTML = originalHTML;
        submitBtn.disabled = false;
    }
});

// Password form submission
document.getElementById('passwordForm')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    // Validate passwords
    if (newPassword !== confirmPassword) {
        window.TrueMeshAuth.showToast('Passwords do not match', 'error');
        return;
    }
    
    if (newPassword.length < 8) {
        window.TrueMeshAuth.showToast('Password must be at least 8 characters', 'error');
        return;
    }
    
    // Check password strength
    const hasUppercase = /[A-Z]/.test(newPassword);
    const hasLowercase = /[a-z]/.test(newPassword);
    const hasNumber = /\d/.test(newPassword);
    
    if (!hasUppercase || !hasLowercase || !hasNumber) {
        window.TrueMeshAuth.showToast('Password must contain uppercase, lowercase, and numbers', 'error');
        return;
    }
    
    const submitBtn = this.querySelector('button[type="submit"]');
    const originalHTML = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Updating...';
    submitBtn.disabled = true;
    
    try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        window.TrueMeshAuth.showToast('Password updated successfully!', 'success');
        
        // Clear form
        this.reset();
    } catch (error) {
        window.TrueMeshAuth.showToast('Failed to update password', 'error');
    } finally {
        submitBtn.innerHTML = originalHTML;
        submitBtn.disabled = false;
    }
});

// Load user data on page load
document.addEventListener('DOMContentLoaded', () => {
    const userData = window.TrueMeshAuth.getUserData();
    
    if (userData) {
        // Populate profile form
        document.getElementById('fullName').value = userData.name || '';
        document.getElementById('phone').value = userData.phone || '';
        document.getElementById('organization').value = userData.organization || '';
        
        // Set last login time
        const tokenTime = localStorage.getItem('truemesh_token_time');
        if (tokenTime) {
            const loginDate = new Date(parseInt(tokenTime));
            document.getElementById('lastLogin').textContent = loginDate.toLocaleString();
        }
    }
});
