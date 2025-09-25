/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html","./src/**/*.{vue,js,ts}"],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Cairo"', '"Poppins"', 'sans-serif'],
        body: ['"Noto Sans Arabic"', '"Inter"', 'sans-serif'],
      },
      colors: {
        brand: {
          primary: 'var(--color-primary)',
          secondary: 'var(--color-secondary)',
          accent: 'var(--color-accent)',
          surface: 'var(--color-surface-elevated)',
        },
      },
      borderRadius: {
        'lg-brand': 'var(--radius-lg)',
        'md-brand': 'var(--radius-md)',
        'sm-brand': 'var(--radius-sm)',
      },
      boxShadow: {
        'brand-lg': 'var(--shadow-lg)',
        'brand-md': 'var(--shadow-md)',
        'brand-sm': 'var(--shadow-sm)',
      },
    },
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: [
      {
        mathleaders: {
          primary: "#0F8A3E",
          "primary-content": "#F3F8F4",
          secondary: "#C8A03B",
          "secondary-content": "#3F2D04",
          accent: "#0D6E8C",
          neutral: "#1A1F16",
          "base-100": "#F7F4EE",
          "base-200": "#FFFFFF",
          info: "#0EA5E9",
          success: "#22C55E",
          warning: "#FACC15",
          error: "#EF4444",
        },
      },
      {
        mathleadersdark: {
          primary: "#25B167",
          "primary-content": "#0C1319",
          secondary: "#D6AF4D",
          "secondary-content": "#1A1202",
          accent: "#1A8FB3",
          neutral: "#0C1319",
          "base-100": "#15202B",
          "base-200": "#1E2A35",
          info: "#38BDF8",
          success: "#4ADE80",
          warning: "#FDE047",
          error: "#F87171",
        },
      },
      "light",
      "dark",
    ],
  },
}
