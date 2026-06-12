import { initDashboardSummary, initAnalyticsChart } from "./features/dashboard.js";
import { initCommandPalette, initLiveSearch } from "./ui/command_palette.js";
import { initDjangoMessageToasts } from "./ui/toast.js";

function initNotificationSocket() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const socketUrl = `${protocol}//${window.location.host}/ws/notifications/`;
    
    const socket = new WebSocket(socketUrl);
    
    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (window.showToast) {
            window.showToast(data.title, data.message, "info");
        } else {
            window.console.log("New Notification:", data);
        }
    };
    
    socket.onclose = () => {
        window.console.log("Notification socket closed. Retrying in 5s...");
        setTimeout(initNotificationSocket, 5000);
    };
}

document.addEventListener("DOMContentLoaded", () => {
    initCommandPalette();
    initLiveSearch();
    initDjangoMessageToasts();
    initDashboardSummary();
    initAnalyticsChart();
    initNotificationSocket();

    if (window.lucide?.createIcons) {
        window.lucide.createIcons();
    }
});
