/** @type {import('tailwindcss').Config} */
module.exports = {
    darkMode: 'class',
    content: [
        './_drafts/**/*.html',
        './_includes/**/*.html',
        './_layouts/**/*.html',
        './_posts/*.md',
        './*.md',
        './*.html',
        './_drafts/**/*.liquid',
        './_includes/**/*.liquid',
        './_layouts/**/*.liquid',
        './_posts/*.liquid',
        './*.liquid',
        './*.liquid',
    ],
    safelist: [
        'hidden', 'sm:table', 'table', 'sm:hidden', 'hover:bg-gray-100',
        'dar:hover:bg-gray-800', 'text-gray-800', 'dark:text-gray-100',
        'group-hover:fill', 'bg-black', 'dark:bg-white', 'font-bold',
        'text-white', 'dark:text-black', 'fill', 'text-white', 'dark:text-black'
    ],
    theme: {
        extend: {
            colors: {
            }
        },
    },
    plugins: [
        require('@tailwindcss/typography'),
    ],
}

