/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: ["./src/**/*.{js,jsx,ts,tsx}", "./public/index.html"],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Barlow Condensed"', "sans-serif"],
        body: ["Inter", "system-ui", "sans-serif"],
        mono: ['"JetBrains Mono"', "monospace"],
      },
      colors: {
        gold: "#E8B923",
        pink: "#E6007A",
        blue: "#007AFF",
        ok: "#3DDC84",
        "ink-0": "#f2f2f4",
        "ink-1": "#e6e6e9",
        "ink-2": "#c7c7cd",
        "ink-3": "#b4b4bb",
        "ink-4": "#8c8c95",
        obsidian: "#050505",
        surface: "#0a0a0d",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        primary: {
          DEFAULT: "#E8B923",
          foreground: "#0a0a0a",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "#E6007A",
          foreground: "#ffffff",
        },
        destructive: {
          DEFAULT: "#ff6b6b",
          foreground: "#ffffff",
        },
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "#E8B923",
        chart: {
          1: "#E8B923",
          2: "#E6007A",
          3: "#007AFF",
          4: "#3DDC84",
          5: "#ff9f43",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: {
            height: "0",
          },
          to: {
            height: "var(--radix-accordion-content-height)",
          },
        },
        "accordion-up": {
          from: {
            height: "var(--radix-accordion-content-height)",
          },
          to: {
            height: "0",
          },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};
