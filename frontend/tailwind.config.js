/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html","./src/**/*.{vue,js,ts}"],
  plugins: [require("daisyui")],
  daisyui: { themes: ["light","dark","cupcake","business","corporate","forest"] },
}
