// Login Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const loginSubmitBtn = document.getElementById('loginSubmitBtn');
    const errorDiv = document.getElementById('loginError');
    
    // Handle form submission
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const role = document.getElementById('role').value;
        
        if (!username || !password || !role) {
            showError('Please fill in all fields.');
            return;
        }
        
        try {
            // Show loading state
            loginSubmitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Logging in...';
            loginSubmitBtn.disabled = true;
            
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password, role })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Login successful, redirect to main page
                showSuccess(`Welcome, ${result.user}! Redirecting...`);
                setTimeout(() => {
                    window.location.href = '/';
                }, 1500);
            } else {
                showError(result.error || 'Login failed. Please try again.');
            }
            
        } catch (error) {
            showError('Connection failed. Please try again.');
            console.error('Login error:', error);
        } finally {
            // Reset button state
            loginSubmitBtn.innerHTML = '<i class="fas fa-sign-in-alt me-2"></i>Login';
            loginSubmitBtn.disabled = false;
        }
    });
    
    function showError(message) {
        errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i>${message}`;
        errorDiv.style.display = 'block';
        errorDiv.className = 'alert alert-danger mt-3';
    }
    
    function showSuccess(message) {
        errorDiv.innerHTML = `<i class="fas fa-check-circle me-2"></i>${message}`;
        errorDiv.style.display = 'block';
        errorDiv.className = 'alert alert-success mt-3';
    }
    
    // Auto-fill demo credentials on click
    document.querySelectorAll('.badge').forEach(badge => {
        badge.addEventListener('click', function() {
            const text = this.textContent;
            if (text.includes('farmer')) {
                document.getElementById('username').value = 'farmer';
                document.getElementById('password').value = 'farmer123';
                document.getElementById('role').value = 'farmer';
            } else if (text.includes('officer')) {
                document.getElementById('username').value = 'officer';
                document.getElementById('password').value = 'officer123';
                document.getElementById('role').value = 'officer';
            } else if (text.includes('user')) {
                document.getElementById('username').value = 'user';
                document.getElementById('password').value = 'user123';
                document.getElementById('role').value = 'normal_user';
            }
        });
    });
});
