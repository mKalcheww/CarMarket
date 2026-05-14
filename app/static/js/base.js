document.addEventListener('DOMContentLoaded', function() {
    
    // --- 1. AI Chat Logic ---
    const chatToggle = document.getElementById('ai-chat-toggle');
    const chatWindow = document.getElementById('ai-chat-window');
    const closeChat = document.getElementById('close-chat');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');

    // Отваряне/Затваряне на чата
    function toggleChat() {
        if (chatWindow.classList.contains('d-none')) {
            chatWindow.classList.remove('d-none');
            setTimeout(() => {
                chatWindow.style.opacity = '1';
                chatWindow.style.transform = 'translateY(0)';
                chatInput.focus();
            }, 10);
            chatToggle.innerHTML = '<i class="bi bi-x-lg fs-4"></i>';
            chatToggle.classList.remove('pulse-neon-btn');
        } else {
            chatWindow.style.opacity = '0';
            chatWindow.style.transform = 'translateY(20px)';
            setTimeout(() => {
                chatWindow.classList.add('d-none');
            }, 300);
            chatToggle.innerHTML = '<i class="bi bi-stars fs-3"></i>';
            chatToggle.classList.add('pulse-neon-btn');
        }
    }

    chatToggle.addEventListener('click', toggleChat);
    closeChat.addEventListener('click', toggleChat);

    // Добавяне на съобщение в UI
    function appendMessage(text, isUser = false) {
        const msgDiv = document.createElement('div');
        msgDiv.className = isUser ? 'user-message' : 'bot-message bg-darker text-white p-3 rounded-3 border border-secondary border-opacity-25';
        if (!isUser) msgDiv.style.alignSelf = 'flex-start';
        msgDiv.style.maxWidth = '85%';
        
        // Използваме textContent за сигурност (XSS защита)
        msgDiv.textContent = text;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Добавяне на индикатор за писане
    function showTyping() {
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.className = 'bot-message bg-darker p-3 rounded-3 border border-secondary border-opacity-25';
        typingDiv.style.alignSelf = 'flex-start';
        typingDiv.innerHTML = '<div class="d-flex"><div class="typing-indicator"></div><div class="typing-indicator"></div><div class="typing-indicator"></div></div>';
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function hideTyping() {
        const typingDiv = document.getElementById('typing-indicator');
        if (typingDiv) typingDiv.remove();
    }

    // Изпращане на съобщение към бекенда
    chatForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const message = chatInput.value.trim();
        if (!message) return;

        // Показваме потребителското съобщение
        appendMessage(message, true);
        chatInput.value = '';
        
        // Показваме индикатора, че AI "мисли"
        showTyping();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();
            hideTyping();

            if (response.ok) {
                appendMessage(data.response);
            } else {
                appendMessage('Опа, възникна грешка: ' + (data.error || 'Сървърът не отговаря.'));
            }
        } catch (error) {
            hideTyping();
            appendMessage('Мрежова грешка. Моля, опитайте отново по-късно.');
            console.error('Chat error:', error);
        }
    });

    // --- 2. Flash Messages Auto-Close Logic ---
    setTimeout(function() {
        const alerts = document.querySelectorAll('.custom-alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 6000);

});