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
            },
            boxShadow: {
                glow: "0 0 0 1px rgba(115,245,200,.1), 0 20px 40px rgba(0,0,0,0.3)",
            },
            animation: {
                float: "float 20s ease-in-out infinite",
                "float-delayed": "float 25s ease-in-out infinite 2s",
            },
            keyframes: {
                float: {
                    "0%, 100%": { transform: "translate(0, 0) scale(1)" },
                    "33%": { transform: "translate(10%, 10%) scale(1.1)" },
                    "66%": { transform: "translate(-5%, 15%) scale(0.9)" },
                },
            },
        },
    },
    plugins: [],
};
