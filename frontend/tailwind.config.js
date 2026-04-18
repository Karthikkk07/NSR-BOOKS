/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0f172a",
        surface: "#1e293b",
        primary: "#4f46e5",
        secondary: "#ec4899",
        textMain: "#f8fafc",
        textMuted: "#94a3b8"
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
