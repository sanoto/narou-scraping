import axios from 'axios'

export const state = () => ({
  parsers: [],
  votingList: [],
  votes: [],
  writerDetail: []
})

export const mutations = {
  setValuesState(state, key, values) {
    state[key] = values
    if (!Array.isArray(state[key])) {
      console.log('state[key] is not array')
      console.error(state[key])
      console.error(state.votingList)
      console.error('state')
      for (const i in state) console.log(typeof i)
    }
  },
  addValueState(state, key, value) {
    if (Array.isArray(state[key])) state[key].push(value)
  },
  updateValueState(state, key, newValue, keyOfPK) {
    if (Array.isArray(state[key])) {
      const index = state[key].findIndex(
        (value) => value[keyOfPK] === newValue[keyOfPK]
      )
      state[key][index] = newValue
    }
  },
  deleteValueState(state, key, valuePK, keyOfPK) {
    if (Array.isArray(state[key]))
      state[key] = state[key].filter((value) => value[keyOfPK] !== valuePK)
  },
  setParsersState(state, parsers) {
    state.parsers = parsers
  },
  addParserState(state, parser) {
    state.parsers.push(parser)
  },
  updateParserState(state, newParser) {
    const index = state.parsers.findIndex(
      (parser) => parser.id === newParser.id
    )
    state.parsers[index] = newParser
  },
  deleteParserState(state, parserID) {
    state.parsers = state.parsers.filter((parser) => parser.id !== parserID)
  }
}

export const actions = {
  async getValues({ commit }, key) {
    if (!this.$isString(key)) return
    const snakeKey = this.$camelToSnake(key)
    const values = await axios
      .get(`api/votes/${snakeKey}/`)
      .then((response) => {
        return response.data.results
      })
      .catch((error) => {
        console.warn(error)
      })
    commit('setValuesState', { key, values })
  },
  async addValue({ commit }, key, value) {
    if (!this.$isString(key)) return
    const snakeKey = this.$camelToSnake(key)
    const newValue = await axios
      .post(`api/votes/${snakeKey}/`, value)
      .then((response) => {
        return response.data
      })
      .catch((error) => {
        console.warn(error)
      })
    commit('addValueState', { key, value: newValue })
  },
  async updateValue({ commit }, key, value, keyOfPK) {
    if (!this.$isString(keyOfPK) || !this.$isString(key)) return
    const snakeKey = this.$camelToSnake(key)
    const newValue = await axios
      .post(`api/votes/${snakeKey}/${value[keyOfPK]}/`, value.regex)
      .then((response) => {
        return response.data
      })
      .catch((error) => {
        console.warn(error)
      })
    commit('updateValueState', { key, newValue, keyOfPK })
  },
  async deleteValue({ commit }, key, valuePK, keyOfPK) {
    if (!this.$isString(keyOfPK) || !this.$isString(key)) return
    const snakeKey = this.$camelToSnake(key)
    await axios.delete(`api/votes/${snakeKey}/${valuePK}/`).catch((error) => {
      console.warn(error)
    })
    commit('deleteValueState', { key, valuePK, keyOfPK })
  },
  async getParsers({ commit }) {
    const parsers = await axios
      .get('api/votes/parser/')
      .then((response) => {
        return response.data.results
      })
      .catch((error) => {
        console.warn(error)
      })
    commit('setParsersState', parsers)
  },
  async addParser({ commit }, regex) {
    const newParser = await axios
      .post('api/votes/parser/', { regex })
      .then((response) => {
        return response.data
      })
      .catch((error) => {
        console.warn(error)
      })
    commit('addParserState', newParser)
  },
  async updateParser({ commit }, parser) {
    const newParser = await axios
      .post(`api/votes/parser/${parser.id}/`, { regex: parser.regex })
      .then((response) => {
        return response.data
      })
      .catch((error) => {
        console.warn(error)
      })
    commit('updateParserState', newParser)
  },
  async deleteParser({ commit }, parserID) {
    await axios.delete(`api/votes/parser/${parserID}/`).catch((error) => {
      console.warn(error)
    })
    commit('deleteParserState', parserID)
  }
}
