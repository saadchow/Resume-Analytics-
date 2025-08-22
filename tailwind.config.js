/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
      "./app/**/*.{js,ts,jsx,tsx,mdx}",
      "./components/**/*.{js,ts,jsx,tsx,mdx}",
      "./pages/**/*.{js,ts,jsx,tsx,mdx}"
    ],
    theme: {
      extend: {
        colors: {
          primary: { 50:"#eff6ff", 500:"#3b82f6", 600:"#2563eb", 700:"#1d4ed8" },
          secondary:{ 50:"#faf5ff", 500:"#a855f7", 600:"#9333ea", 700:"#7c3aed" }
        },
        animation: {
          "pulse-slow": "pulse 3s cubic-bezier(0.4,0,0.6,1) infinite",
          "bounce-subtle": "bounce 2s infinite"
        }
      }
    },
    plugins: []
  };
  