import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.config/
export default defineConfig({
  plugins: [
    react(),
    // This config is essential for Tailwind v4.
    // It maps your CSS variables to the utility classes
    // that your components (Formcards.jsx, App.jsx) are using.
    tailwindcss({
      theme: {
        extend: {
          fontFamily: {
            serif: 'var(--font-serif)',
          },
          boxShadow: {
            soft: 'var(--shadow-soft)',
            'soft-dark': 'var(--shadow-soft-dark)',
          },
          colors: {
            accent: 'var(--color-accent)',
            primary: 'var(--color-primary)',

            // Light Mode
            'text-light': 'var(--color-text-light)',
            'subtle-light': 'var(--color-subtle-light)',
            'border-light': 'var(--color-border-light)',
            'card-light': 'var(--color-card-light)',
            'background-light': 'var(--color-background-light)',

            // Dark Mode
            'text-dark': 'var(--color-text-dark)',
            'subtle-dark': 'var(--color-subtle-dark)',
            'border-dark': 'var(--color-border-dark)',
            'card-dark': 'var(--color-card-dark)',
            'background-dark': 'var(--color-background-dark)',
          },
        },
      },
    }),
  ],
})