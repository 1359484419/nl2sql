/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: '#0f1117',
        surface: '#1a1d27',
        surface2: '#13161f',
        border: '#2d3348',
        primary: '#7c6af7',
        green: '#34d399',
        orange: '#fb923c',
        yellow: '#fbbf24',
        blue: '#60a5fa',
        red: '#f87171',
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
