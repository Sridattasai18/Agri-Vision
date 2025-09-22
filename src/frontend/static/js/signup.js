// Signup Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const signupForm = document.getElementById('signupForm');
    const signupSubmitBtn = document.getElementById('signupSubmitBtn');
    const errorDiv = document.getElementById('signupError');
    const successDiv = document.getElementById('signupSuccess');
    const togglePasswordBtn = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    
    // Password visibility toggle
    togglePasswordBtn.addEventListener('click', function() {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        
        const icon = this.querySelector('i');
        icon.classList.toggle('fa-eye');
        icon.classList.toggle('fa-eye-slash');
    });
    
    // Real-time password validation
    passwordInput.addEventListener('input', function() {
        document.getElementById('password-strength').style.display = 'block';
        validatePassword();
    });
    
    confirmPasswordInput.addEventListener('input', function() {
        validatePasswordMatch();
    });
    
    // Handle form submission
    signupForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = {
            firstName: document.getElementById('firstName').value.trim(),
            lastName: document.getElementById('lastName').value.trim(),
            email: document.getElementById('email').value.trim(),
            username: document.getElementById('username').value.trim(),
            password: document.getElementById('password').value,
            confirmPassword: document.getElementById('confirmPassword').value,
            role: document.getElementById('role').value,
            termsAccepted: document.getElementById('termsCheck').checked
        };
        
        // Validate form
        if (!validateForm(formData)) {
            return;
        }
        
        try {
            // Show loading state
            signupSubmitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Creating Account...';
            signupSubmitBtn.disabled = true;
            
            const response = await fetch('/api/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                showSuccess('Account created successfully! Redirecting to login...');
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);
            } else {
                showError(result.error || 'Signup failed. Please try again.');
            }
            
        } catch (error) {
            showError('Connection failed. Please try again.');
            console.error('Signup error:', error);
        } finally {
            // Reset button state
            signupSubmitBtn.innerHTML = '<i class="fas fa-user-plus me-2"></i>Create Account';
            signupSubmitBtn.disabled = false;
        }
    });
    
    function validateForm(data) {
        // Clear previous errors
        hideMessages();
        
        let isValid = true;

        if (!data.firstName || !data.lastName || !data.email || !data.username || !data.password || !data.confirmPassword || !data.role) {
            showError('Please fill in all required fields.');
            return false;
        }

        if (data.password !== data.confirmPassword) {
            showError('Passwords do not match.');
            return false;
        }

        if (data.password.length < 8) {
            showError('Password must be at least 8 characters long.');
            return false;
        }

        if (!data.termsAccepted) {
            showError('You must accept the terms and conditions.');
            return false;
        }
        
        return isValid;
    }
    
    function validatePassword() {
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;
        
        // Update password strength indicator
        const strength = getPasswordStrength(password);
        updatePasswordStrength(strength);
        
        // Check if passwords match
        if (confirmPassword && password !== confirmPassword) {
            confirmPasswordInput.classList.add('is-invalid');
        } else {
            confirmPasswordInput.classList.remove('is-invalid');
        }
    }
    
    function validatePasswordMatch() {
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;
        
        if (confirmPassword && password !== confirmPassword) {
            confirmPasswordInput.classList.add('is-invalid');
        } else {
            confirmPasswordInput.classList.remove('is-invalid');
        }
    }
    
    function getPasswordStrength(password) {
        let strength = 0;
        
        if (password.length >= 8) strength++;
        if (/[a-z]/.test(password)) strength++;
        if (/[A-Z]/.test(password)) strength++;
        if (/[0-9]/.test(password)) strength++;
        if (/[^A-Za-z0-9]/.test(password)) strength++;
        
        return strength;
    }
    
    function updatePasswordStrength(strength) {
        const strengthBar = document.getElementById('password-strength-bar');
        const strengthLevels = {
            0: { width: '0%', class: 'bg-danger' },
            1: { width: '20%', class: 'bg-danger' },
            2: { width: '40%', class: 'bg-warning' },
            3: { width: '60%', class: 'bg-warning' },
            4: { width: '80%', class: 'bg-success' },
            5: { width: '100%', class: 'bg-success' }
        };

        const { width, class: newClass } = strengthLevels[strength] || strengthLevels[0];

        strengthBar.style.width = width;
        strengthBar.className = 'progress-bar'; // Reset classes
        strengthBar.classList.add(newClass);
        
        // Optional: Add valid/invalid classes to input
        passwordInput.classList.remove('is-valid', 'is-invalid');
        if (strength >= 4) {
            passwordInput.classList.add('is-valid');
        } else if (passwordInput.value.length > 0) {
            passwordInput.classList.add('is-invalid');
        }
    }
    
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    function showError(message) {
        errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i>${message}`;
        errorDiv.style.display = 'block';
        successDiv.style.display = 'none';
    }
    
    function showSuccess(message) {
        successDiv.innerHTML = `<i class="fas fa-check-circle me-2"></i>${message}`;
        successDiv.style.display = 'block';
        errorDiv.style.display = 'none';
    }
    
    function hideMessages() {
        errorDiv.style.display = 'none';
        successDiv.style.display = 'none';
    }
});
