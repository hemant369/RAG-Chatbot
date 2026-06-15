module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{ts,tsx,js,jsx}"
  ],
  theme: {
    extend: {
      colors: {
        accent: {
          50: "#f5f3ff",
          100: "#ede9fe",
          500: "#7c3aed",
          700: "#6d28d9"
        },
        bg: "#0b1220",
        panel: "#0f1724"
      },
      borderRadius: {
        card: "14px"
      }
    }
  },
  plugins: []
};