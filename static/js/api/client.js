function getCookie(name) {
    const cookies = document.cookie ? document.cookie.split(";") : [];
    for (const cookie of cookies) {
        const trimmed = cookie.trim();
        if (trimmed.startsWith(`${name}=`)) {
            return decodeURIComponent(trimmed.slice(name.length + 1));
        }
    }
    return "";
}

export function getCsrfToken() {
    return getCookie("csrftoken");
}

export async function apiFetch(url, options = {}) {
    const method = (options.method || "GET").toUpperCase();
    const isWriteMethod = !["GET", "HEAD", "OPTIONS", "TRACE"].includes(method);

    const headers = new Headers(options.headers || {});
    if (!headers.has("Accept")) {
        headers.set("Accept", "application/json");
    }

    const hasJsonBody = options.body && !(options.body instanceof FormData);
    if (hasJsonBody && !headers.has("Content-Type")) {
        headers.set("Content-Type", "application/json");
    }

    if (isWriteMethod && !headers.has("X-CSRFToken")) {
        headers.set("X-CSRFToken", getCsrfToken());
    }

    const response = await fetch(url, {
        ...options,
        method,
        headers,
        credentials: "same-origin",
    });

    const contentType = response.headers.get("Content-Type") || "";
    const payload = contentType.includes("application/json") ? await response.json() : await response.text();

    if (!response.ok) {
        const error = new Error("API request failed.");
        error.status = response.status;
        error.payload = payload;
        throw error;
    }

    return payload;
}

window.devhubApi = {
    apiFetch,
    getCsrfToken,
};
