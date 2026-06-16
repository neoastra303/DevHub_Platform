// ─── Debounce Helper ───
function debounce(fn, delay = 150) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
    };
}

// ─── Count-Up Animation (IntersectionObserver) ───
document.addEventListener("DOMContentLoaded", () => {
    const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const els = document.querySelectorAll("[data-count-up]");
    if (prefersReduced) {
        els.forEach(el => {
            const target = parseInt(el.dataset.countUp, 10);
            if (isNaN(target)) return;
            const format = (n) => {
                if (el.dataset.format === "currency") return "$" + n.toLocaleString();
                if (el.dataset.format === "percent") return n + "%";
                return n.toLocaleString();
            };
            el.textContent = format(target);
        });
        return;
    }

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (!entry.isIntersecting) return;
            const el = entry.target;
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
            observer.unobserve(el);
        });
    }, { threshold: 0.3 });

    els.forEach(el => observer.observe(el));
});

// ─── Button Ripple Effect (Mouse + Keyboard) ───
function createRipple(btn, x, y) {
    const rect = btn.getBoundingClientRect();
    const ripple = document.createElement("span");
    ripple.className = "ripple-effect";
    const size = Math.max(rect.width, rect.height);
    ripple.style.width = ripple.style.height = size + "px";
    ripple.style.left = (x - rect.left - size / 2) + "px";
    ripple.style.top = (y - rect.top - size / 2) + "px";
    btn.appendChild(ripple);
    ripple.addEventListener("animationend", () => ripple.remove());
}

document.addEventListener("click", (e) => {
    const btn = e.target.closest(".ripple-container");
    if (!btn) return;
    createRipple(btn, e.clientX, e.clientY);
});

document.addEventListener("keydown", (e) => {
    if (e.key !== "Enter" && e.key !== " ") return;
    const btn = e.target.closest(".ripple-container");
    if (!btn) return;
    const rect = btn.getBoundingClientRect();
    createRipple(btn, rect.left + rect.width / 2, rect.top + rect.height / 2);
});

// ─── Page Transition (HTMX) ───
document.addEventListener("htmx:beforeSwap", () => {
    document.querySelector("#main-content")?.classList.add("page-exiting");
});
document.addEventListener("htmx:afterSettle", () => {
    document.querySelector("#main-content")?.classList.remove("page-exiting");
});

// ─── Filter / Search Items (Debounced) ───
window.filterItems = debounce(function(query, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    const items = container.querySelectorAll("[data-filter-item]");
    const q = query.toLowerCase().trim();
    items.forEach(item => {
        const text = (item.dataset.filterText || item.textContent).toLowerCase();
        item.style.display = (!q || text.includes(q)) ? "" : "none";
    });
});

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
