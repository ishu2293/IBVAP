/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        command: {
          bg: '#0b0f19',
          card: '#111827',
          border: '#1f2937',
          header: '#0f172a',
          accent: '#10b981',
          highlight: '#3b82f6',
          alert: '#ef4444',
          warning: '#f59e0b'
        }
      }
    },
  },
  plugins: [],
}
