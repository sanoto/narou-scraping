export default ({ app }, inject) => {
  inject('isString', (a) => typeof a === 'string' || a instanceof String)

  inject('camelToSnake', (p) => {
    // 大文字を_+小文字にする(例:A を _a)
    // if (isString(p))
    return p.replace(/([A-Z])/g, (s) => '_' + s.charAt(0).toLowerCase())
    // else {
    //   console.error('camelToSnake error ' + p.toString())
    //   return null
    // }
  })
}
