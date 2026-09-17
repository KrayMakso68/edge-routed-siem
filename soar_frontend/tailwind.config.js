/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        kibana: {
          bg: '#f5f7fa',
          sidebar: '#ffffff',
          text: '#343741',
          primary: '#006bb4',
          border: '#d3dae6',
          dark_bg: '#1a1b25',
          dark_sidebar: '#21222c',
        }
      }
    },
  },
  plugins: [],
}
