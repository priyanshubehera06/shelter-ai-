/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0d1117",
        surface: "#161b22",
        "surface-raised": "#21262d",
        "surface-border": "#30363d",
        primary: {
          DEFAULT: "#10b981", // Green accent for eco / passive thermal
          hover: "#059669",
          light: "#34d399",
          dark: "#047857"
        },
        solar: {
          DEFAULT: "#f59e0b",
          light: "#fbbf24"
        },
        thermal: {
          hot: "#ef4444",
          warm: "#f97316",
          comfortable: "#10b981",
          cold: "#3b82f6"
        },
        climate: {
          DEFAULT: "#38bdf8",
          dark: "#0284c7"
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      }
    },
  },
  plugins: [],
}
