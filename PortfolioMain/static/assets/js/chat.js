document.addEventListener('DOMContentLoaded', () => {
    const chatBtn = document.getElementById('chat-widget-btn');
    const chatWindow = document.getElementById('chat-window');
    const closeBtn = document.getElementById('chat-close-btn');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('chat-send-btn');
    const chatBody = document.getElementById('chat-body');
    const typingIndicator = document.getElementById('typing-indicator');

    // Toggle Chat Window
    function toggleChat() {
        chatWindow.classList.toggle('active');
        if (chatWindow.classList.contains('active')) {
            setTimeout(() => chatInput.focus(), 300);
        }
    }

    chatBtn.addEventListener('click', toggleChat);
    closeBtn.addEventListener('click', toggleChat);

    // Append Message to Chat Body
    function appendMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);
        messageDiv.textContent = text;

        // Insert before typing indicator
        chatBody.insertBefore(messageDiv, typingIndicator);

        // Scroll to bottom
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    // Send Message Logic
    async function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        // Clear input
        chatInput.value = '';

        // Add user message
        appendMessage(message, 'user');

        // Show typing indicator
        typingIndicator.classList.add('active');
        chatBody.scrollTop = chatBody.scrollHeight;

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();

            // Hide typing indicator
            typingIndicator.classList.remove('active');

            if (data.response) {
                appendMessage(data.response, 'bot');
            } else if (data.error) {
                appendMessage("Sorry, something went wrong. Please try again.", 'bot');
                console.error('Chat API Error:', data.error);
            }

        } catch (error) {
            console.error('Network Error:', error);
            typingIndicator.classList.remove('active');
            appendMessage("Network error. Please check your connection.", 'bot');
        }
    }

    // Event Listeners for Sending
    sendBtn.addEventListener('click', sendMessage);

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault(); // Prevent background scrolling/form submission
            e.stopPropagation();
            sendMessage();
        }
    });
});
