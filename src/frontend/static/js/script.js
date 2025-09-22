// AgriVision Frontend JavaScript

// Global variables
let currentUser = null;
let currentCropData = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    checkUserSession();
});

// Initialize application
function initializeApp() {
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href.startsWith('#')) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    const y = target.getBoundingClientRect().top + window.pageYOffset - document.querySelector('.navbar').offsetHeight;
                    window.scrollTo({ top: y, behavior: 'smooth' });
                }
            }
        });
    });

    // Handle navbar transparency on scroll
    const mainNav = document.getElementById('mainNav');
    if (mainNav) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                mainNav.classList.add('navbar-scrolled');
            } else {
                mainNav.classList.remove('navbar-scrolled');
            }
        });
    }

    // Add fade-in animation to sections
    const sections = document.querySelectorAll('section');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    });

    sections.forEach(section => {
        observer.observe(section);
    });
}

// Setup event listeners
function setupEventListeners() {
    // Crop recommendation form
    document.getElementById('cropForm').addEventListener('submit', handleCropRecommendation);
    
    // Sample data button
    document.getElementById('fillSampleData').addEventListener('click', fillSampleData);
    
    // Weather form
    document.getElementById('weatherForm').addEventListener('submit', handleWeatherRequest);
    
    // Logout button
    document.getElementById('logoutBtn')?.addEventListener('click', handleLogout);
    
    // Chatbot functionality
    document.getElementById('sendChatBtn').addEventListener('click', () => handleChatbotMessage());
    document.getElementById('chatInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleChatbotMessage();
        }
    });

    // Feedback form
    const fbForm = document.getElementById('feedbackForm');
    if (fbForm) {
        fbForm.addEventListener('submit', handleFeedbackSubmit);
    }
}

// Handle crop recommendation
async function handleCropRecommendation(e) {
    e.preventDefault();
    
    const submitBtn = document.getElementById('cropSubmitBtn');
    const originalText = submitBtn.innerHTML;
    
    try {
        // Show loading state
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Analyzing...';
        submitBtn.disabled = true;
        
        // Get form data
        const formData = new FormData(e.target);
        const data = {
            N: parseFloat(formData.get('N')),
            P: parseFloat(formData.get('P')),
            K: parseFloat(formData.get('K')),
            temperature: parseFloat(formData.get('temperature')),
            humidity: parseFloat(formData.get('humidity')),
            ph: parseFloat(formData.get('ph')),
            rainfall: parseFloat(formData.get('rainfall'))
        };
        
        // Make API request
        const response = await fetch('/api/predict/crop', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayCropResults(result);
            currentCropData = data; // Store for fertilizer recommendation
        } else {
            showError('Crop Recommendation', result.error);
        }
        
    } catch (error) {
        showError('Crop Recommendation', 'Failed to get crop recommendation. Please try again.');
        console.error('Error:', error);
    } finally {
        // Reset button state
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

// Display crop results
function displayCropResults(result) {
    const resultsDiv = document.getElementById('cropResults');
    const resultsBody = document.getElementById('cropResultsBody');
    
    let html = '<div class="row">';
    
    result.predictions.forEach((crop, index) => {
        const isRecommended = index === 0;
        const badgeClass = isRecommended ? 'bg-success' : 'bg-secondary';
        const cardClass = isRecommended ? 'border-success' : '';
        
        html += `
            <div class="col-md-4 mb-3">
                <div class="card crop-card h-100 ${cardClass}" onclick="getFertilizerRecommendation('${crop.crop}')" style="cursor: pointer;">
                    <div class="card-body text-center">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <h6 class="card-title mb-0">${crop.crop.charAt(0).toUpperCase() + crop.crop.slice(1)}</h6>
                            <span class="badge ${badgeClass}">${isRecommended ? 'Recommended' : 'Alternative'}</span>
                        </div>
                        <div class="probability-badge">
                            ${(crop.probability * 100).toFixed(1)}% Match 
                        </div>
                        <small class="text-muted mt-2 d-block">Click for fertilizer info</small>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    
    resultsBody.innerHTML = html;
    resultsDiv.style.display = 'block';
    
    // Scroll to results
    resultsDiv.scrollIntoView({ behavior: 'smooth' });
}

// Get fertilizer recommendation
async function getFertilizerRecommendation(crop) {
    if (!currentCropData) {
        showError('Fertilizer Recommendation', 'Please get a crop recommendation first.');
        return;
    }
    
    try {
        const data = {
            crop: crop,
            N: currentCropData.N,
            P: currentCropData.P,
            K: currentCropData.K
        };
        
        const response = await fetch('/api/predict/fertilizer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayFertilizerResults(crop, result.data);
        } else {
            showError('Fertilizer Recommendation', result.error);
        }
        
    } catch (error) {
        showError('Fertilizer Recommendation', 'Failed to get fertilizer recommendation.');
        console.error('Error:', error);
    }
}

// Display fertilizer results
function displayFertilizerResults(crop, data) {
    const resultsDiv = document.getElementById('fertilizerResults');
    
    let html = `
        <div class="card fertilizer-card">
            <div class="card-header bg-warning text-dark">
                <h5 class="mb-0">
                    <i class="fas fa-flask me-2"></i>Fertilizer Recommendation for ${crop.charAt(0).toUpperCase() + crop.slice(1)}
                </h5>
            </div>
            <div class="card-body">
    `;
    
    if (data.error) {
        html += `<div class="alert alert-danger">${data.error}</div>`;
    } else if (data.message) {
        html += `<div class="alert alert-success">${data.message}</div>`;
    } else {
        html += `
            <div class="row">
                <div class="col-md-6">
                    <h6>Nutrient Deficiency</h6>
                    <p class="mb-2"><strong>Type:</strong> ${data.type}</p>
                    <p class="mb-2"><strong>Deficiency:</strong> ${data.deficiency} units</p>
                </div>
                <div class="col-md-6">
                    <h6>Recommendation</h6>
                    <p class="mb-2">${data.recommendation}</p>
                    <span class="fertilizer-type">${data.fertilizer_type}</span>
                </div>
            </div>
        `;
    }
    
    html += `
            </div>
        </div>
    `;
    
    resultsDiv.innerHTML = html;
    
    // Scroll to fertilizer section
    document.getElementById('fertilizer').scrollIntoView({ behavior: 'smooth' });
}

// Handle weather request
async function handleWeatherRequest(e) {
    e.preventDefault();
    
    const city = document.getElementById('city').value;
    const submitBtn = document.getElementById('weatherSubmitBtn');
    const originalText = submitBtn.innerHTML;
    
    try {
        // Show loading state
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
        submitBtn.disabled = true;
        
        // Fetch 7-day forecast
        const response = await fetch('/api/weather/forecast', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ city: city })
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayForecastResults(result.data);
        } else {
            showError('Weather Information', result.error);
        }
        
    } catch (error) {
        showError('Weather Information', 'Failed to get weather data. Please try again.');
        console.error('Error:', error);
    } finally {
        // Reset button state
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

// Display 7-day forecast results
function displayForecastResults(data) {
    const resultsDiv = document.getElementById('weatherResults');
    
    if (!data || data.error) {
        resultsDiv.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>${data?.error || 'Unable to load forecast'}
            </div>
        `;
    } else {
        const city = data.city;
        const country = data.country || '';
        const days = data.days || [];

        let cards = days.map(d => {
            const date = new Date(typeof d.dt === 'number' ? d.dt * 1000 : d.dt);
            const dayName = date.toLocaleDateString(undefined, { weekday: 'short' });
            const icon = getWeatherIcon(d.description || d.weather_code);
            return `
            <div class="forecast-card">
                <div class="meta mb-1">${dayName}</div>
                <div class="icon"><i class="fas ${icon}"></i></div>
                <div class="temp mb-1">${Math.round(d.temp_max)}° / ${Math.round(d.temp_min)}°C</div>
                <div class="meta">${d.humidity}% humidity</div>
                <div class="text-capitalize meta mt-1">${(d.description || '')}</div>
            </div>`;
        }).join('');

        resultsDiv.innerHTML = `
            <div class="card weather-card">
                <div class="card-body">
                    <h5 class="mb-3"><i class="fas fa-location-dot me-2"></i>${city}${country ? ', ' + country : ''}</h5>
                    <div class="forecast-grid">${cards}</div>
                </div>
            </div>
        `;
    }
    
    resultsDiv.style.display = 'block';
}

// Get weather icon based on description
function getWeatherIcon(description) {
    // WMO Weather interpretation codes (from Open-Meteo)
    const code = Number(description); // The API sends weather_code, not text
    if (code === 0) return 'fa-sun'; // Clear sky
    if (code >= 1 && code <= 3) return 'fa-cloud-sun'; // Mainly clear, partly cloudy, overcast
    if (code === 45 || code === 48) return 'fa-smog'; // Fog
    if (code >= 51 && code <= 57) return 'fa-cloud-rain'; // Drizzle
    if (code >= 61 && code <= 67) return 'fa-cloud-showers-heavy'; // Rain
    if (code >= 71 && code <= 77) return 'fa-snowflake'; // Snow
    if (code >= 80 && code <= 82) return 'fa-cloud-showers-heavy'; // Rain showers
    if (code >= 95 && code <= 99) return 'fa-bolt'; // Thunderstorm

    // Fallback for text-based descriptions from current weather API
    const text = String(description).toLowerCase();
    if (text.includes('clear')) return 'fa-sun';
    if (text.includes('cloud')) return 'fa-cloud';
    if (text.includes('rain')) return 'fa-cloud-rain';
    if (text.includes('storm')) return 'fa-bolt';
    if (text.includes('snow')) return 'fa-snowflake';
    if (text.includes('fog') || text.includes('mist')) return 'fa-smog';
    
    return 'fa-cloud-sun'; // Default icon
}

// Fill sample data
function fillSampleData() {
    document.getElementById('N').value = '90';
    document.getElementById('P').value = '40';
    document.getElementById('K').value = '40';
    document.getElementById('temperature').value = '20.5';
    document.getElementById('humidity').value = '80';
    document.getElementById('ph').value = '6.5';
    document.getElementById('rainfall').value = '200';
}

// Handle Smart Farmer chatbot message
async function handleChatbotMessage(messageText = null) {
    const chatInput = document.getElementById('chatInput');
    const message = messageText || chatInput.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addMessageToChat(message, 'user');
    if (!messageText) {
        chatInput.value = '';
    }
    
    // Show typing indicator
    showTypingIndicator();
    renderSuggestions([]); // Clear suggestions
    
    try {
        const response = await fetch('/api/chatbot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });
        
        const result = await response.json();
        hideTypingIndicator();
        
        if (result.success) {
            addMessageToChat(result.response, 'bot');
            renderSuggestions(result.suggestions);
        } else {
            addMessageToChat(result.error || 'Sorry, I encountered an error. Please try again.', 'bot');
        }
        
    } catch (error) {
        hideTypingIndicator();
        addMessageToChat('Sorry, I\'m having trouble connecting. Please try again later.', 'bot');
        console.error('Smart Farmer chatbot error:', error);
    }
}

// Add message to chat with enhanced styling
function addMessageToChat(message, sender) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const now = new Date();
    const timeString = now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    
    let avatarIcon, avatarClass;
    if (sender === 'user') {
        avatarIcon = 'fa-user';
        avatarClass = 'bg-info';
    } else {
        avatarIcon = 'fa-robot';
        avatarClass = 'bg-success';
    }
    
    messageDiv.innerHTML = `
        <div class="message-avatar ${avatarClass}">
            <i class="fas ${avatarIcon}"></i>
        </div>
        <div class="message-content">
            <div class="message-header">
                <strong>${sender === 'user' ? 'You' : 'Smart Farmer'}</strong>
                <small class="text-muted ms-2">${timeString}</small>
            </div>
            <div class="message-text">${formatMessage(message)}</div>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Render suggestion buttons
function renderSuggestions(suggestions) {
    const suggestionsContainer = document.getElementById('chatSuggestions');
    suggestionsContainer.innerHTML = '';
    if (!suggestions || suggestions.length === 0) {
        return;
    }

    suggestions.forEach(text => {
        const button = document.createElement('button');
        button.className = 'suggestion-btn';
        button.textContent = text;
        button.onclick = () => handleChatbotMessage(text);
        suggestionsContainer.appendChild(button);
    });
}

// Format message with proper line breaks and lists
function formatMessage(message) {
    // Convert line breaks to HTML
    let formatted = message.replace(/\n/g, '<br>');
    
    // Convert bullet points to HTML lists
    if (formatted.includes('•') || formatted.includes('-')) {
        formatted = formatted.replace(/([•-])\s*(.+)/g, '<li>$2</li>');
        if (formatted.includes('<li>')) {
            formatted = '<ul>' + formatted + '</ul>';
        }
    }
    
    return formatted;
}

// Show typing indicator
function showTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typingIndicator';
    typingDiv.className = 'message bot-message typing-indicator';
    
    typingDiv.innerHTML = `
        <div class="message-avatar bg-success">
            <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
            <div class="message-header">
                <strong>Smart Farmer</strong>
                <small class="text-muted ms-2">typing...</small>
            </div>
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Hide typing indicator
function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Check user session
async function checkUserSession() {
    try {
        const response = await fetch('/api/user');
        const result = await response.json();
        
        if (result.success) {
            currentUser = result;
            updateUIForUser();
        }
    } catch (error) {
        console.log('No active session');
    }
}

// Update UI for logged in user
function updateUIForUser() {
    if (currentUser) {
        // The logout button is part of the main navigation and should always be present
        // when the user is on the main page.
        document.getElementById('logoutBtn').innerHTML = `<i class="fas fa-sign-out-alt me-2"></i>Logout (${currentUser.user})`;
    }
}

// Handle logout
async function handleLogout() {
    try {
        await fetch('/api/logout', { method: 'POST' });
        currentUser = null;
        // Redirect to login page
        window.location.href = '/';
    } catch (error) {
        console.error('Logout error:', error);
        // Force redirect even if API call fails
        window.location.href = '/';
    }
}

// Show error message
function showError(title, message) {
    showToast(title, message, 'danger');
}

// Show success message
function showSuccess(title, message) {
    showToast(title, message, 'success');
}

// Generic toast notification function
function showToast(title, message, type = 'info') {
    const toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) return;

    const toastId = 'toast-' + Date.now();
    const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-triangle';

    const toastHTML = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header bg-${type} text-white">
                <i class="fas ${icon} me-2"></i>
                <strong class="me-auto">${title}</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;

    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { delay: 5000 });
    toast.show();
    toastElement.addEventListener('hidden.bs.toast', () => toastElement.remove());
}

// Utility function to format numbers
function formatNumber(num, decimals = 2) {
    return parseFloat(num).toFixed(decimals);
}

// Handle feedback form submission
async function handleFeedbackSubmit(e) {
    e.preventDefault();
    const name = document.getElementById('fb_name').value.trim();
    const email = document.getElementById('fb_email').value.trim();
    const message = document.getElementById('fb_message').value.trim();
    try {
        const res = await fetch('/api/feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, message })
        });
        const result = await res.json();
        if (result.success) {
            showSuccess('Feedback Submitted', 'Thank you for your feedback!');
            e.target.reset();
        } else {
            showError('Feedback Error', result.error || 'Please try again.');
        }
    } catch (err) {
        console.error('Feedback error', err);
        showError('Connection Error', 'Unable to submit feedback right now.');
    }
}