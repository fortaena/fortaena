export default [
  {
    files: ["**/*.{js,jsx,mjs,cjs}"],
    languageOptions: {
      ecmaVersion: 2024,
      sourceType: "module",
    },
    rules: {
      "no-unused-vars": ["error", { "argsIgnorePattern": "^_", "varsIgnorePattern": "^_" }],
      "no-console": "off",
      "no-redeclare": "off",
      "no-undef": "off",
    },
  },
  {
    ignores: ["node_modules/", ".git/", ".next/", ".open-next/", ".wrangler/", "tailwind.config.js", "postcss.config.js", "**/*.ts", "**/*.tsx"],
  },
];