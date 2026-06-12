import { apiFetch } from "../api/client.js";

function updateMetric(metricName, value) {
    const metricNode = document.querySelector(`[data-dashboard-metric="${metricName}"]`);
    if (!metricNode) {
        return;
    }
    metricNode.textContent = value;
}

export async function initDashboardSummary() {
    const root = document.querySelector("[data-dashboard-summary]");
    if (!root) {
        return;
    }

    try {
        const payload = await apiFetch("/api/v1/devhub/dashboard-summary/");
        updateMetric("points", payload.points ?? 0);
        updateMetric("active_projects", payload.active_projects ?? 0);
        updateMetric("reputation", payload.reputation ?? 0);
        updateMetric("total_post_views", payload.total_post_views ?? 0);
    } catch (error) {
        window.console.error("Failed to hydrate dashboard summary.", error);
    }
}
