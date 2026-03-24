import type { Config } from "tailwindcss";

export default {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        oatey: {
          brown: "#5c4033",
          cream: "#f5f5dc",
          yellow: "#f9d71c",
          dark: "#2d1b0d",
          light: "#fffaf0",
          accent: "#d97706",
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
