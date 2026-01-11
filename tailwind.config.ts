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
        // PCB-inspired color palette
        trace: {
          50: "#f0fdf4",
          100: "#dcfce7",
          200: "#bbf7d0",
          300: "#86efac",
          400: "#4ade80",
          500: "#22c55e", // Primary - soldermask green
          600: "#16a34a",
          700: "#15803d",
          800: "#166534",
          900: "#14532d",
          950: "#052e16",
        },
        copper: {
          50: "#fffbeb",
          100: "#fef3c7",
          200: "#fde68a",
          300: "#fcd34d",
          400: "#fbbf24", // Copper trace highlight
          500: "#f59e0b",
          600: "#d97706",
          700: "#b45309",
          800: "#92400e",
          900: "#78350f",
          950: "#451a03",
        },
        substrate: {
          50: "#fafaf9",
          100: "#f5f5f4",
          200: "#e7e5e4",
          300: "#d6d3d1",
          400: "#a8a29e",
          500: "#78716c",
          600: "#57534e",
          700: "#44403c",
          800: "#292524",
          900: "#1c1917",
          950: "#0c0a09",
        },
        silkscreen: "#ffffff",
        solder: "#c0c0c0",
      },
      fontFamily: {
        mono: [
          "SF Mono",
          "Monaco",
          "Cascadia Code",
          "Roboto Mono",
          "Fira Code",
          "monospace",
        ],
        sans: [
          "Inter",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Roboto",
          "sans-serif",
        ],
      },
      backgroundImage: {
        "grid-pattern":
          "linear-gradient(to right, rgba(34, 197, 94, 0.03) 1px, transparent 1px), linear-gradient(to bottom, rgba(34, 197, 94, 0.03) 1px, transparent 1px)",
        "trace-gradient":
          "linear-gradient(135deg, #22c55e 0%, #16a34a 50%, #15803d 100%)",
        "copper-gradient":
          "linear-gradient(135deg, #fbbf24 0%, #f59e0b 50%, #d97706 100%)",
        "dark-gradient":
          "radial-gradient(ellipse at top, #171717 0%, #0a0a0a 100%)",
      },
      backgroundSize: {
        grid: "24px 24px",
      },
      boxShadow: {
        trace: "0 0 20px rgba(34, 197, 94, 0.15)",
        "trace-lg": "0 0 40px rgba(34, 197, 94, 0.2)",
        copper: "0 0 20px rgba(251, 191, 36, 0.15)",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "trace-flow": "traceFlow 2s ease-in-out infinite",
      },
      keyframes: {
        traceFlow: {
          "0%, 100%": { opacity: "0.5" },
          "50%": { opacity: "1" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
