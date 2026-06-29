/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,ts,jsx,tsx,md,mdx}'],
  theme: {
    extend: {
      colors: {
        codec:       '#ffb600',
        'line-1':    '#ff5555',
        'line-2':    '#a451ff',
        'line-3':    '#00a6b0',
        transversal: '#d400aa',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
};
