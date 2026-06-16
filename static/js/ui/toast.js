const TOAST_CONTAINER_ID = "toast-container";

function createToastContainer() {
    const container = document.createElement("div");
    container.id = TOAST_CONTAINER_ID;
    container.className = "fixed bottom-20 md:bottom-6 right-6 z-50 flex flex-col items-end pointer-events-none max-w-sm w-full px-6";
    document.body.appendChild(container);
    return container;
}

export function showToast(message, type = "info") {
    const container = document.getElementById(TOAST_CONTAINER_ID) || createToastContainer();
    const toast = document.createElement("div");
    toast.className =
        "glass-card rounded-2xl px-6 py-4 mb-3 shadow-glow border-l-4 transition-all duration-500 transform translate-x-full opacity-0";
    toast.setAttribute("role", "alert");
    toast.setAttribute("aria-live", "assertive");

    const colors = {
        success: "border-mint",
        error: "border-coral",
        info: "border-white/20",
    };

    toast.classList.add(colors[type] || colors.info);
    toast.innerHTML = `
        <div class="flex items-center gap-3">
            <i data-lucide="${type === "success" ? "check-circle" : type === "error" ? "alert-circle" : "info"}" class="w-5 h-5" aria-hidden="true"></i>
            <span class="font-medium">${message}</span>
        </div>
    `;

    container.appendChild(toast);
    if (window.lucide?.createIcons) {
        window.lucide.createIcons();
    }

    setTimeout(() => {
        toast.classList.remove("translate-x-full", "opacity-0");
    }, 10);

    setTimeout(() => {
        toast.classList.add("translate-x-full", "opacity-0");
        setTimeout(() => toast.remove(), 500);
    }, 4000);
}

export function initDjangoMessageToasts() {
    const messages = document.querySelectorAll(".django-message");
    messages.forEach((messageElement) => {
        const toastType = messageElement.dataset.type === "error" ? "error" : "success";
        showToast(messageElement.innerText, toastType);
        messageElement.remove();
    });
}

window.showToast = showToast;
