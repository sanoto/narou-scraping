module.exports = {
  root: true,
  env: {
    browser: true,
    node: true
  },
  extends: [
    '@nuxtjs',
    '@nuxtjs/eslint-config-typescript',
    'prettier',
    'prettier/vue',
    'plugin:prettier/recommended',
    'prettier/@typescript-eslint',
    'plugin:nuxt/recommended'
  ],
  plugins: [
    'prettier'
  ],
  // add your custom rules here
  rules: {
    'semi': [2, 'never'],
    'no-console': 'off',
    'vue/max-attributes-per-line': 'off',

    'no-unused-vars': 'off',
    '@typescript-eslint/no-unused-vars': 'off',
    "no-extra-semi": "off",
    "@typescript-eslint/no-extra-semi": "error",
    "quotes": "off",
    "@typescript-eslint/quotes": ["error", "single", {
      "avoidEscape": true,
      "allowTemplateLiterals": true
    }],

    'prettier/prettier': ['error', {
      'semi': false,
      "arrowParens": "always",
      "singleQuote": true,
      "trailingComma": "es5"
    }]
  }
}
