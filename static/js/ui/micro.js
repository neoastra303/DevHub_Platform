// ─── Count-Up Animation ───
document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-count-up]").forEach(el => {
        const target = parseInt(el.dataset.countUp, 10);
        if (isNaN(target)) return;
        const duration = parseInt(el.dataset.duration, 10) || 800;
        const start = performance.now();

        const format = (n) => {
            if (el.dataset.format === "currency") return "$" + n.toLocaleString();
            if (el.dataset.format === "percent") return n + "%";
            return n.toLocaleString();
        };

        const tick = (now) => {
            const progress = Math.min((now - start) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            const current = Math.round(eased * target);
            el.textContent = format(current);
            if (progress < 1) requestAnimationFrame(tick);
            else el.textContent = format(target);
        };
        requestAnimationFrame(tick);
    });
});

// ─── Button Ripple Effect ───
document.addEventListener("click", (e) => {
    const btn = e.target.closest(".ripple-container");
    if (!btn) return;
    const rect = btn.getBoundingClientRect();
    const ripple = document.createElement("span");
    ripple.className = "ripple-effect";
    const size = Math.max(rect.width, rect.height);
    ripple.style.width = ripple.style.height = size + "px";
    ripple.style.left = (e.clientX - rect.left - size / 2) + "px";
    ripple.style.top = (e.clientY - rect.top - size / 2) + "px";
    btn.appendChild(ripple);
    ripple.addEventListener("animationend", () => ripple.remove());
});

// ─── Page Transition (HTMX) ───
document.addEventListener("htmx:beforeSwap", () => {
    document.querySelector("#main-content")?.classList.add("opacity-0", "translate-y-4");
});
document.addEventListener("htmx:afterSwap", () => {
    const main = document.querySelector("#main-content");
    if (!main) return;
    main.classList.remove("opacity-0", "translate-y-4");
    main.classList.add("transition-all", "duration-500", "ease-out");
    requestAnimationFrame(() => {
        main.classList.remove("opacity-0", "translate-y-4");
    });
});

// ─── Filter / Search Items ───
window.filterItems = function(query, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    const items = container.querySelectorAll("[data-filter-item]");
    const q = query.toLowerCase().trim();
    items.forEach(item => {
        const text = (item.dataset.filterText || item.textContent).toLowerCase();
        item.style.display = (!q || text.includes(q)) ? "" : "none";
    });
};

// ─── Tooltip Toggle ───
document.addEventListener("mouseenter", (e) => {
    const el = e.target.closest("[data-tooltip]");
    if (!el) return;
    const text = el.dataset.tooltip;
    if (!text) return;
    const tip = document.createElement("div");
    tip.className = "fixed z-50 px-3 py-1.5 rounded-xl bg-elevated border border-white/10 text-xs font-bold text-slate-200 shadow-soft pointer-events-none animate-scale-in";
    tip.textContent = text;
    document.body.appendChild(tip);
    const rect = el.getBoundingClientRect();
    tip.style.left = (rect.left + rect.width / 2 - tip.offsetWidth / 2) + "px";
    tip.style.top = (rect.top - tip.offsetHeight - 8) + "px";
    el._tooltip = tip;
}, true);
document.addEventListener("mouseleave", (e) => {
    const el = e.target.closest("[data-tooltip]");
    if (el && el._tooltip) {
        el._tooltip.remove();
        el._tooltip = null;
    }
}, true);
