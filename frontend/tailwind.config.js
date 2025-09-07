/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // VEDYA Color Theme - Knowledge Power Digital Illustrations About Science
        vedya: {
          pink: '#F27ECA',      // Science-1 (Primary accent)
          purple: '#8857F2',    // Science-2 (Primary brand)
          darkPurple: '#6C45BF', // Science-3 (Dark brand)
          yellow: '#F2E30F',    // Science-4 (Bright accent)
          orange: '#F2B90F',    // Science-5 (Warm accent)
        },
        // Semantic color mappings
        primary: {
          50: '#faf5ff',
          100: '#f3e8ff',
          500: '#8857F2',  // Science-2
          600: '#6C45BF',  // Science-3
          700: '#553581',
          900: '#1a0b2e',
        },
        accent: {
          pink: '#F27ECA',   // Science-1
          yellow: '#F2E30F', // Science-4
          orange: '#F2B90F', // Science-5
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'float': 'float 3s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
    },
  },
  plugins: [],
}
