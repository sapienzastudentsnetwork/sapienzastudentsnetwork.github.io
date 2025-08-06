/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'selector',
  content: [
    "layouts/**/*.{html,js}",
    "cybersec/**/*.md",
    "compsci/**/*.md",
    "acsai/**/*.md",
    "it/**/*.md",
  ],
  theme: {
    extend: {
        colors: {
            'primary': '#132441',
            'primary-dark': '#021330',
            'accent': '#ffffff',
            'diamond': '#2d58b5',
            'faint': '#264281',
            // 'faint': '#2d58b5'
        }
    },
  },
  safelist: [],
  plugins: [require("@tailwindcss/typography")],
};
