// Application State
let messages = [];
let isLoading = false;

// DOM Elements
const welcomeScreen     = document.getElementById('welcomeScreen');
const messagesContainer = document.getElementById('messagesContainer');
const loadingIndicator  = document.getElementById('loadingIndicator');
const messagesEnd       = document.getElementById('messagesEnd');
const clearBtn          = document.getElementById('clearBtn');
const chatForm          = document.getElementById('chatForm');
const messageInput      = document.getElementById('messageInput');
const sendButton        = document.getElementById('sendButton');
const sendIcon          = document.getElementById('sendIcon');
const loadingSpinner    = document.getElementById('loadingSpinner');
const languageSelect    = document.getElementById('languageSelect');

// Initialize
document.addEventListener('DOMContentLoaded', function () {
    setupEventListeners();
    updateSendButton();
    setupWelcomeChips();
});

// Clicking a welcome chip pre-fills the textarea
function setupWelcomeChips() {
    document.querySelectorAll('.welcome-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            messageInput.value = chip.textContent.trim();
            autoResizeTextarea();
            updateSendButton();
            messageInput.focus();
        });
    });
}

function setupEventListeners() {
    chatForm.addEventListener('submit', handleSubmit);
    clearBtn.addEventListener('click', clearChat);
    messageInput.addEventListener('input', handleInputChange);
    messageInput.addEventListener('keydown', handleKeyDown);
}

function handleSubmit(e) {
    e.preventDefault();
    const content = messageInput.value.trim();
    if (!content || isLoading) return;
    sendMessage(content);
}

function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSubmit(e);
    }
}

function handleInputChange() {
    autoResizeTextarea();
    updateSendButton();
}

function autoResizeTextarea() {
    messageInput.style.height = 'auto';
    const newHeight = Math.min(messageInput.scrollHeight, 128);
    messageInput.style.height = newHeight + 'px';
}

function updateSendButton() {
    const hasContent = messageInput.value.trim().length > 0;
    sendButton.disabled = !hasContent || isLoading;
}

async function sendMessage(content) {
    const userMessage = {
        id: Date.now().toString(),
        content: content,
        type: 'user',
        timestamp: new Date()
    };
    messages.push(userMessage);
    displayMessage(userMessage);

    messageInput.value = '';
    messageInput.style.height = 'auto';
    hideWelcomeScreen();
    showClearButton();
    setLoadingState(true);

    try {
        const response = await fetch('/generate-tanaga', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_input: content,
                language: languageSelect.value
            }),
        });

        const data = await response.json();
        const isError = !data.reply
            || data.reply.startsWith('Error:')
            || data.reply.startsWith('System Error:');

        const aiMessage = {
            id: (Date.now() + 1).toString(),
            content: data.reply || 'No response received.',
            type: 'ai',
            language: data.metadata ? data.metadata.language : null,
            meterValid: data.metadata ? data.metadata.meter.all_match : null,
            timestamp: new Date(),
            isError: isError
        };
        messages.push(aiMessage);
        displayMessage(aiMessage);

    } catch (error) {
        const errorMessage = {
            id: (Date.now() + 1).toString(),
            content: 'Error: ' + error.message,
            type: 'ai',
            timestamp: new Date(),
            isError: true
        };
        messages.push(errorMessage);
        displayMessage(errorMessage);

    } finally {
        setLoadingState(false);
    }
}

function displayMessage(message) {
    const messageEl = document.createElement('div');
    messageEl.className = 'message ' + message.type;

    const time = message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    const avatarIcon = message.type === 'user'
        ? '<span class="material-symbols-outlined" style="font-size:15px;">person</span>'
        : '<span class="material-symbols-outlined" style="font-size:15px;">smart_toy</span>';

    const languageBadge = message.language
        ? '<span class="message-model">' + message.language + '</span>'
        : '';

    const meterBadge = (message.meterValid !== null && message.meterValid !== undefined)
        ? '<span class="meter-badge ' + (message.meterValid ? 'meter-valid' : 'meter-invalid') + '">'
          + (message.meterValid ? '✓ meter' : '⚠ meter off') + '</span>'
        : '';

    const senderLabel = message.type === 'user' ? 'You' : 'Tanaga Agent';

    messageEl.innerHTML = [
        '<div class="message-wrapper">',
            '<div class="message-header">',
                '<div class="message-avatar">' + avatarIcon + '</div>',
                '<div class="message-info">',
                    '<span class="message-sender">' + senderLabel + '</span>',
                    languageBadge,
                '</div>',
            '</div>',
            '<div class="message-bubble">',
                '<div class="message-text">' + message.content + '</div>',
            '</div>',
            '<div class="message-footer">',
                '<span>' + time + '</span>',
                meterBadge,
            '</div>',
        '</div>'
    ].join('');

    messagesContainer.appendChild(messageEl);
    scrollToBottom();
}

function setLoadingState(loading) {
    isLoading = loading;
    updateSendButton();
    messageInput.disabled = loading;
    if (loading) {
        loadingIndicator.style.display = 'flex';
        sendIcon.style.display = 'none';
        loadingSpinner.style.display = 'block';
    } else {
        loadingIndicator.style.display = 'none';
        sendIcon.style.display = 'block';
        loadingSpinner.style.display = 'none';
    }
    if (loading) scrollToBottom();
}

function hideWelcomeScreen() { welcomeScreen.style.display = 'none'; }
function showWelcomeScreen() { welcomeScreen.style.display = 'flex'; }
function showClearButton()   { clearBtn.style.display = 'flex'; }
function hideClearButton()   { clearBtn.style.display = 'none'; }

function clearChat() {
    messages = [];
    messagesContainer.innerHTML = '';
    showWelcomeScreen();
    hideClearButton();
    setLoadingState(false);
    updateSendButton();
}

function scrollToBottom() {
    messagesEnd.scrollIntoView({ behavior: 'smooth' });
}
