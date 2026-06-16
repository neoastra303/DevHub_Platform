function openCommandPalette() {
    window.dispatchEvent(new CustomEvent("open-command-palette"));
}

function closeCommandPalette() {
    window.dispatchEvent(new CustomEvent("close-command-palette"));
}

export function initCommandPalette() {
    window.addEventListener("keydown", (event) => {
        const key = event.key.toLowerCase();
        if ((event.ctrlKey || event.metaKey) && key === "k") {
            event.preventDefault();
            openCommandPalette();
        } else if (event.key === "Escape") {
            closeCommandPalette();
        }
    });
}

function filterItems(query, containerId) {
    const container = document.getElementById(containerId);
    if (!container) {
        return;
    }

    const items = container.querySelectorAll("article");
    const normalizedQuery = query.toLowerCase();

    items.forEach((item) => {
        const text = item.innerText.toLowerCase();
        if (text.includes(normalizedQuery)) {
            item.style.display = "block";
            item.classList.add("animate-in");
        } else {
            item.style.display = "none";
        }
    });
}

export function initLiveSearch() {
    // Uses the generic [data-filter-item] filter from micro.js
}
