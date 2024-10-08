/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'selector',
  content: [
    "layouts/**/*.{html,js}",
    "29932/**/*.md",
    "30786/**/*.md",
    "it/**/*.md",
  ],
  theme: {
    extend: {
        colors: {
            'primary': '#132441',
            'primary-dark': '#021330',
            'accent': '#ffffff'
        }
    },
  },
  safelist: [],
  plugins: [require("@tailwindcss/typography")],
};
