/**
 * DevHub Platform Client Utilities
 * Handles: Toast notifications, Command Palette (Ctrl+K), and UI enhancements.
 */

// --- Toast System ---
window.showToast = (message, type = 'info') => {
    const container = document.getElementById('toast-container') || createToastContainer();
    const toast = document.createElement('div');
    toast.className = `glass-card rounded-2xl px-6 py-4 mb-3 shadow-glow border-l-4 transition-all duration-500 transform translate-x-full opacity-0`;
    
    const colors = {
        success: 'border-mint',
        error: 'border-coral',
        info: 'border-white/20'
    };
    
    toast.classList.add(colors[type] || colors.info);
    toast.innerHTML = `
        <div class="flex items-center gap-3">
            <i data-lucide="${type === 'success' ? 'check-circle' : type === 'error' ? 'alert-circle' : 'info'}" class="w-5 h-5"></i>
            <span class="font-medium">${message}</span>
        </div>
    `;
    
    container.appendChild(toast);
    lucide.createIcons();
    
    // Animate in
    setTimeout(() => {
        toast.classList.remove('translate-x-full', 'opacity-0');
    }, 10);
    
    // Auto-remove
    setTimeout(() => {
        toast.classList.add('translate-x-full', 'opacity-0');
        setTimeout(() => toast.remove(), 500);
    }, 4000);
};

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'fixed bottom-6 right-6 z-50 flex flex-col items-end pointer-events-none max-w-sm w-full px-6';
    document.body.appendChild(container);
    return container;
}

// --- Command Palette Logic ---
window.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const palette = document.getElementById('command-palette');
        if (palette) {
            palette.__x_model.set(true); // Specific to Alpine.js implementation
        }
    }
});

// --- Live Search Logic ---
window.filterItems = (query, containerId) => {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const items = container.querySelectorAll('article');
    const lowerQuery = query.toLowerCase();
    
    items.forEach(item => {
        const text = item.innerText.toLowerCase();
        if (text.includes(lowerQuery)) {
            item.style.display = 'block';
            item.classList.add('animate-in');
        } else {
            item.style.display = 'none';
        }
    });
};

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    // Check for Django messages to convert to toasts
    const messages = document.querySelectorAll('.django-message');
    messages.forEach(msg => {
        const type = msg.dataset.type === 'error' ? 'error' : 'success';
        window.showToast(msg.innerText, type);
        msg.remove();
    });
});
