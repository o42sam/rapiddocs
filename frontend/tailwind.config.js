/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx,html}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#e6eeff',
          100: '#d5e5ff',  // From logo light blue
          200: '#aaccff',
          300: '#77aaff',
          400: '#4477dd',
          500: '#0055cc',
          600: '#0044aa',  // From logo primary blue
          700: '#003388',
          800: '#002266',
          900: '#001144',
        },
      },
      fontFamily: {
        sans: ['"Liberation Serif"', 'Georgia', 'serif'],
        serif: ['"Liberation Serif"', 'Georgia', 'serif'],
      },
    },
  },
  plugins: [],
}
