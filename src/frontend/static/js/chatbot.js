/**
 * AgriVision Chatbot Widget
 * AI-powered farming assistant using Google Gemini
 */

class AgriChatbot {
    constructor() {
        this.isOpen = false;
        this.messages = [];
        this.sessionId = null;
        this.init();
    }

    init() {
        this.createChatWidget();
        this.attachEventListeners();
        this.loadChatHistory();
    }

    createChatWidget() {
        const chatHTML = `
            <!-- Chatbot Toggle Button -->
            <button id="chatbot-toggle" class="chatbot-toggle" aria-label="Toggle Chatbot">
                <i class="fas fa-comments"></i>
                <span class="chatbot-badge">AI</span>
            </button>

            <!-- Chatbot Widget -->
            <div id="chatbot-widget" class="chatbot-widget">
                <div class="chatbot-header">
                    <div class="chatbot-header-content">
                        <div class="chatbot-avatar">
                            <i class="fas fa-robot"></i>
                        </div>
                        <div class="chatbot-title">
                            <h4>AgriBot</h4>
                            <span class="chatbot-status">
                                <span class="status-dot"></span>
                                Online
                            </span>
                        </div>
                    </div>
                    <button class="chatbot-close" aria-label="Close Chatbot">
                        <i class="fas fa-times"></i>
                    </button>
                </div>

                <div class="chatbot-messages" id="chatbot-messages">
                    <div class="chatbot-welcome">
                        <div class="welcome-icon">
                            <i class="fas fa-seedling"></i>
                        </div>
                        <h5>Welcome to AgriBot! 🌱</h5>
                        <p>I'm your AI farming assistant. I can help you with:</p>
                        <ul>
                            <li>Crop recommendations</li>
                            <li>Fertilizer advice</li>
                            <li>Weather insights</li>
                            <li>Soil management tips</li>
                        </ul>
                    </div>
                </div>

                <div class="chatbot-suggestions" id="chatbot-suggestions">
                    <!-- Suggestions will be added here dynamically -->
                </div>

                <div class="chatbot-input-container">
                    <div class="chatbot-input-wrapper">
                        <textarea 
                            id="chatbot-input" 
                            class="chatbot-input" 
                            placeholder="Ask me anything about farming..."
                            rows="1"
                        ></textarea>
                        <button id="chatbot-send" class="chatbot-send" aria-label="Send Message">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                    <div class="chatbot-footer-text">
                        Powered by Google Gemini AI
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', chatHTML);
    }

    attachEventListeners() {
        const toggle = document.getElementById('chatbot-toggle');
        const close = document.querySelector('.chatbot-close');
        const sendBtn = document.getElementById('chatbot-send');
        const input = document.getElementById('chatbot-input');

        toggle.addEventListener('click', () => this.toggleChat());
        close.addEventListener('click', () => this.toggleChat());
        sendBtn.addEventListener('click', () => this.sendMessage());
        
        // Send on Enter, new line on Shift+Enter
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Auto-resize textarea
        input.addEventListener('input', () => this.autoResizeTextarea(input));
    }

    toggleChat() {
        this.isOpen = !this.isOpen;
        const widget = document.getElementById('chatbot-widget');
        const toggle = document.getElementById('chatbot-toggle');

        if (this.isOpen) {
            widget.classList.add('active');
            toggle.classList.add('active');
            document.getElementById('chatbot-input').focus();
        } else {
            widget.classList.remove('active');
            toggle.classList.remove('active');
        }
    }

    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    async sendMessage() {
        const input = document.getElementById('chatbot-input');
        const message = input.value.trim();

        if (!message) return;

        // Add user message to UI
        this.addMessage(message, 'user');
        input.value = '';
        input.style.height = 'auto';

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // Send to backend
            const response = await fetch('/api/chatbot', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message })
            });

            const data = await response.json();

            // Remove typing indicator
            this.removeTypingIndicator();

            if (data.success) {
                // Add bot response
                this.addMessage(data.response, 'bot');

                // Show suggestions if available
                if (data.suggestions && data.suggestions.length > 0) {
                    this.showSuggestions(data.suggestions);
                }

                // Save to history
                this.saveToHistory(message, data.response);
            } else {
                this.addMessage('Sorry, I encountered an error. Please try again.', 'bot', true);
            }
        } catch (error) {
            console.error('Chatbot error:', error);
            this.removeTypingIndicator();
            this.addMessage('Sorry, I\'m having trouble connecting. Please check your internet connection and try again.', 'bot', true);
        }
    }

    addMessage(text, sender, isError = false) {
        const messagesContainer = document.getElementById('chatbot-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `chatbot-message ${sender}-message ${isError ? 'error-message' : ''}`;

        const avatar = sender === 'bot' 
            ? '<div class="message-avatar"><i class="fas fa-robot"></i></div>'
            : '<div class="message-avatar"><i class="fas fa-user"></i></div>';

        const time = new Date().toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit',
            hour12: true 
        });

        messageDiv.innerHTML = `
            ${avatar}
            <div class="message-content">
                <div class="message-text">${this.formatMessage(text)}</div>
                <div class="message-time">${time}</div>
            </div>
        `;

        messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    formatMessage(text) {
        // Convert markdown-style formatting to HTML
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
        text = text.replace(/\n/g, '<br>');
        
        // Convert bullet points
        text = text.replace(/^• (.+)$/gm, '<li>$1</li>');
        if (text.includes('<li>')) {
            text = text.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
        }

        return text;
    }

    showTypingIndicator() {
        const messagesContainer = document.getElementById('chatbot-messages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chatbot-message bot-message typing-indicator';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = `
            <div class="message-avatar"><i class="fas fa-robot"></i></div>
            <div class="message-content">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();
    }

    removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    showSuggestions(suggestions) {
        const container = document.getElementById('chatbot-suggestions');
        container.innerHTML = '';

        suggestions.forEach(suggestion => {
            const chip = document.createElement('button');
            chip.className = 'suggestion-chip';
            chip.textContent = suggestion;
            chip.addEventListener('click', () => {
                document.getElementById('chatbot-input').value = suggestion;
                this.sendMessage();
            });
            container.appendChild(chip);
        });
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('chatbot-messages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    saveToHistory(userMessage, botResponse) {
        const history = JSON.parse(localStorage.getItem('agribot_history') || '[]');
        history.push({
            user: userMessage,
            bot: botResponse,
            timestamp: new Date().toISOString()
        });
        // Keep only last 50 messages
        if (history.length > 50) {
            history.shift();
        }
        localStorage.setItem('agribot_history', JSON.stringify(history));
    }

    loadChatHistory() {
        const history = JSON.parse(localStorage.getItem('agribot_history') || '[]');
        // Load last 5 messages
        const recentHistory = history.slice(-5);
        recentHistory.forEach(item => {
            this.addMessage(item.user, 'user');
            this.addMessage(item.bot, 'bot');
        });
    }
}

// Initialize chatbot when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.agriChatbot = new AgriChatbot();
});
