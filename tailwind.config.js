module.exports = {
    content: ["./templates/**/*.html", "./static/js/**/*.js"],
    theme: {
        extend: {
            colors: {
                ink: "#08111b",
                mint: "#73f5c8",
                coral: "#ff8e6e",
                storm: "#112032",
                edge: "#203248",
                surface: "#112032",
                elevated: "#1a2e44",
                success: "#73f5c8",
                danger: "#ff8e6e",
                warning: "#fbbf24",
                info: "#60a5fa",
            },
            boxShadow: {
                glow: "0 0 0 1px rgba(115,245,200,.1), 0 20px 40px rgba(0,0,0,0.3)",
                "glow-lg": "0 0 0 1px rgba(115,245,200,.15), 0 30px 60px rgba(0,0,0,0.4)",
                "glow-coral": "0 0 0 1px rgba(255,142,110,.1), 0 20px 40px rgba(0,0,0,0.3)",
                soft: "0 4px 20px rgba(0,0,0,0.2)",
            },
            fontFamily: {
                display: ['"Segoe UI"', "system-ui", "-apple-system", "sans-serif"],
                mono: ['"Cascadia Code"', '"Fira Code"', "Consolas", "monospace"],
            },
            fontSize: {
                "2xs": ["0.625rem", { lineHeight: "0.875rem" }],
            },
            animation: {
                float: "float 20s ease-in-out infinite",
                "float-delayed": "float 25s ease-in-out infinite 2s",
                "count-up": "count-up 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards",
                "fade-in": "fade-in 0.4s ease-out forwards",
                "slide-up": "slide-up 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards",
                "scale-in": "scale-in 0.2s ease-out forwards",
                "pulse-soft": "pulse-soft 2s ease-in-out infinite",
                ripple: "ripple 0.6s linear",
            },
            keyframes: {
                float: {
                    "0%, 100%": { transform: "translate(0, 0) scale(1)" },
                    "33%": { transform: "translate(10%, 10%) scale(1.1)" },
                    "66%": { transform: "translate(-5%, 15%) scale(0.9)" },
                },
                "count-up": {
                    "0%": { opacity: "0", transform: "translateY(8px)" },
                    "100%": { opacity: "1", transform: "translateY(0)" },
                },
                "fade-in": {
                    "0%": { opacity: "0" },
                    "100%": { opacity: "1" },
                },
                "slide-up": {
                    "0%": { opacity: "0", transform: "translateY(16px)" },
                    "100%": { opacity: "1", transform: "translateY(0)" },
                },
                "scale-in": {
                    "0%": { opacity: "0", transform: "scale(0.95)" },
                    "100%": { opacity: "1", transform: "scale(1)" },
                },
                "pulse-soft": {
                    "0%, 100%": { opacity: "1" },
                    "50%": { opacity: "0.5" },
                },
                ripple: {
                    "0%": { transform: "scale(0)", opacity: "0.5" },
                    "100%": { transform: "scale(4)", opacity: "0" },
                },
            },
        },
    },
    plugins: [],
};
