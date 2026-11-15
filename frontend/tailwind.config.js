/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        warm: {
          50: '#FDFBF7',
          100: '#F9F8F5',
          200: '#F0ECE1',
          300: '#E4DDD0',
          bg: '#FAFAF9',
          surface: '#FFFFFF',
          border: '#E2E8F0',
          muted: '#64748B',
        },
        lpu: {
          primary: '#E05A1B', // LPU Signature Terracotta/Orange
          dark: '#B8400C',
          light: '#FFF5F0',
          border: '#FED7AA',
          navy: '#0F172A',
        }
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      boxShadow: {
        'soft-sm': '0 1px 2px 0 rgba(0, 0, 0, 0.03)',
        'soft': '0 2px 8px -2px rgba(0, 0, 0, 0.05), 0 1px 4px -1px rgba(0, 0, 0, 0.03)',
        'soft-md': '0 6px 16px -4px rgba(0, 0, 0, 0.06), 0 2px 6px -2px rgba(0, 0, 0, 0.03)',
        'soft-lg': '0 12px 32px -8px rgba(0, 0, 0, 0.08), 0 4px 12px -2px rgba(0, 0, 0, 0.04)',
      }
    },
  },
  plugins: [],
}

