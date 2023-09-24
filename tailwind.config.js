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
    ],
    safelist: [
        'hidden',
        'sm:table',
        'table',
        'sm:hidden',
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

