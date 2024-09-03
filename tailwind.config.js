/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "layouts/**/*.{html,js}",
    "29932/**/*.{md}",
    "30786/**/*.{md}",
    "it/**/*.{md}",
  ],
  theme: {
    extend: {},
  },
  safelist: [],
  plugins: [require("@tailwindcss/typography")],
};
