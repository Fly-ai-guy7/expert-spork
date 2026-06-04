/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#11214d",
          50: "#f4f6fb",
          100: "#e8eef9",
          900: "#0a173a",
        },
        role: {
          prosecution: "#11214d",
          defense: "#f43f5e",
          judicial: "#10b981",
          trainee: "#f59e0b",
        },
      },
      fontFamily: {
        sans: ['"Inter"', "system-ui", "sans-serif"],
        arabic: ['"Noto Naskh Arabic"', '"Amiri"', "serif"],
      },
    },
  },
  plugins: [],
};
