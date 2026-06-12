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

export async function initAnalyticsChart() {
    const canvas = document.getElementById("engagementChart");
    if (!canvas) {
        return;
    }

    try {
        const payload = await apiFetch("/api/v1/devhub/analytics/");
        new Chart(canvas, {
            type: "line",
            data: {
                labels: payload.labels,
                datasets: payload.datasets.map(ds => ({
                    ...ds,
                    borderColor: "#00ffa3",
                    backgroundColor: "rgba(0, 255, 163, 0.1)",
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: "#00ffa3",
                    pointBorderColor: "#08111b",
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                }))
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: "#162231",
                        titleFont: { size: 12, weight: "bold" },
                        bodyFont: { size: 12 },
                        padding: 12,
                        cornerRadius: 12,
                        displayColors: false,
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: "#64748b", font: { size: 10 } }
                    },
                    y: {
                        grid: { color: "rgba(255, 255, 255, 0.05)" },
                        ticks: { color: "#64748b", font: { size: 10 }, stepSize: 10 }
                    }
                }
            }
        });
    } catch (error) {
        window.console.error("Failed to initialize analytics chart.", error);
    }
}
