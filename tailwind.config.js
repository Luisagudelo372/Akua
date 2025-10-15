/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./core/templates/**/*.html",   // todas tus plantillas
    "./core/**/*.js",              // si usas JS que tenga clases
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
