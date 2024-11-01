import js from "@eslint/js";

export default [
  {
    files: [
      "app/assets/**/*.mjs"
    ],
    rules: {
      ...js.configs.recommended.rules,
      "semi": ["error", "always"],
      "no-prototype-builtins": "warn",
      "no-unused-vars": "warn",
      "no-extra-boolean-cast": "warn",
      "no-undef": "warn",
      "no-useless-escape": "warn",
      "no-unexpected-multiline": "warn",
      //needs more standardjs rules
    },
  },
  {
    files: ["**/*.mjs"],
    languageOptions: {
      sourceType: "module"
    }
  },
];