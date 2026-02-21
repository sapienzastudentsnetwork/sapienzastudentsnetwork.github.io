/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ['selector', '[data-theme="dark"]'],
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
            'primary': 'rgb(var(--tw-primary-rgb) / <alpha-value>)',
            'primary-dark': '#021330',
            'accent': 'rgb(var(--tw-accent-rgb) / <alpha-value>)',
            'diamond': 'rgb(var(--tw-diamond-rgb) / <alpha-value>)',
            'faint': 'rgb(var(--tw-faint-rgb) / <alpha-value>)',
        }
    },
  },
  safelist: [],
  plugins: [require("@tailwindcss/typography")],
};
