module.exports = {
  // add your custom config here
  // https://stylelint.io/user-guide/configuration
  plugins: ['stylelint-prettier'],
  extends: ['stylelint-prettier/recommended'],
  rules: {
    'prettier/prettier': true,
  },
}
