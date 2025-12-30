import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{ts,tsx}", "./src/**/*.tsx"],
  theme: {
    extend: {
      fontFamily: {
        display: ["Inter", "system-ui", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "sans-serif"],
      },
      colors: {
        brand: {
          50: "#f5f8ff",
          100: "#e3edfe",
          200: "#c8d9ff",
          500: "#3558ff",
          600: "#1d3ae8",
        },
      },
      boxShadow: {
        card: "0 10px 25px rgba(15, 23, 42, 0.08)",
      },
    },
  },
  plugins: [],
};

export default config;
