import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        neu: {
          bg: {
            primary: '#e6e7f0',
            secondary: '#f0f1f7',
          },
          shadow: {
            light: '#ffffff',
            dark: '#c8c9d4',
          },
          accent: {
            DEFAULT: '#8b7fc7',
            deep: '#6b5eb0',
          },
          text: {
            primary: '#4a4a5e',
            secondary: '#7a7a8e',
          },
          success: '#7bc89d',
        },
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'sans-serif'],
      },
      boxShadow: {
        'neu-convex': '8px 8px 16px #c8c9d4, -8px -8px 16px #ffffff',
        'neu-convex-hover': '12px 12px 24px #c8c9d4, -12px -12px 24px #ffffff',
        'neu-concave': 'inset 6px 6px 12px #c8c9d4, inset -6px -6px 12px #ffffff',
        'neu-flat': '4px 4px 8px #c8c9d4, -4px -4px 8px #ffffff',
        'neu-pressed': 'inset 4px 4px 8px #c8c9d4, inset -4px -4px 8px #ffffff',
        'neu-accent': '6px 6px 12px rgba(139, 127, 199, 0.3), -6px -6px 12px rgba(255, 255, 255, 0.5)',
        'neu-accent-hover': '8px 8px 16px rgba(139, 127, 199, 0.4), -8px -8px 16px rgba(255, 255, 255, 0.6)',
      },
      borderRadius: {
        neu: '24px',
        'neu-lg': '32px',
        'neu-button': '16px',
      },
      animation: {
        float: 'float 3s ease-in-out infinite',
        spin: 'spin 1.5s linear infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        spin: {
          to: { transform: 'rotate(360deg)' },
        },
      },
      transitionTimingFunction: {
        'neu-bounce': 'cubic-bezier(0.34, 1.56, 0.64, 1)',
      },
    },
  },
  plugins: [],
};

export default config;
