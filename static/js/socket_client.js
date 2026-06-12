import { initDashboardSummary, initAnalyticsChart } from "./features/dashboard.js";
import { initCommandPalette, initLiveSearch } from "./ui/command_palette.js";
import { initDjangoMessageToasts } from "./ui/toast.js";

document.addEventListener("DOMContentLoaded", () => {
    initCommandPalette();
    initLiveSearch();
    initDjangoMessageToasts();
    initDashboardSummary();
    initAnalyticsChart();

    if (window.lucide?.createIcons) {
        window.lucide.createIcons();
    }
});
