/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.{html,js}", "./node_modules/flowbite/**/*.js"],
  theme: {
    extend: {
      spacing: {
        18: "4.5rem",
        20: "5rem",
        22: "5.5rem",
        24: "6rem",
        // Add more custom spacing values as needed
      },
    },
  },
  plugins: [require("flowbite/plugin")],
};
