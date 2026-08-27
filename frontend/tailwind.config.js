/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        "background": "var(--background)",
        "on-background": "var(--on-background)",
        "surface-bright": "var(--surface-bright)",
        "on-surface": "var(--on-surface)",
        "on-surface-variant": "var(--on-surface-variant)",
        "primary": "var(--primary)",
        "on-primary": "var(--on-primary)",
        "primary-container": "var(--primary-container)",
        "on-primary-container": "var(--on-primary-container)",
        "secondary": "var(--secondary)",
        "on-secondary": "var(--on-secondary)",
        "secondary-container": "var(--secondary-container)",
        "on-secondary-container": "var(--on-secondary-container)",
        "error": "var(--error)",
        "on-error": "var(--on-error)",
        "success-green": "var(--success-green)",
        "energy-coral": "var(--energy-coral)",
        "electric-violet": "var(--electric-violet)",
        "deep-indigo": "var(--deep-indigo)",
        "diksha-blue": "var(--diksha-blue)",
        "surface-cream": "var(--surface-cream)",
        "outline-variant": "var(--outline-variant)",
        "surface-container-lowest": "var(--surface-container-lowest)",
        "surface-container-low": "var(--surface-container-low)",
        "surface-container": "var(--surface-container)",
        "surface-container-high": "var(--surface-container-high)",
        "surface-container-highest": "var(--surface-container-highest)",
      },
      borderRadius: {
        "DEFAULT": "0.25rem",
        "lg": "0.5rem",
        "xl": "0.75rem",
        "2xl": "1rem",
        "full": "9999px"
      },
      spacing: {
        "unit": "8px",
        "container-max": "1280px",
        "margin-desktop": "40px",
        "gutter": "24px",
        "margin-mobile": "16px"
      },
      fontFamily: {
        sans: ["Be Vietnam Pro", "sans-serif"],
        body: ["Be Vietnam Pro", "sans-serif"],
      }
    },
  },
  plugins: [],
}
