import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#EBF0FF",
          100: "#C7D4FF",
          500: "#1A56DB",
          600: "#1447B8",
          700: "#103898",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      animation: {
        "spin-slow": "spin 2s linear infinite",
        "pulse-soft": "pulse 2.5s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};

export default config;
