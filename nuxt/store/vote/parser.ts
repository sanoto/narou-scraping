import { VuexModule, Module, Mutation, Action } from 'vuex-module-decorators'

import { BaseRestModule } from '~/store/base'

export interface Parser {
  regex: string
}

@Module({ stateFactory: true, namespaced: true, name: 'parser' })
export class ParserModule extends BaseRestModule<Parser, number> {
  url: string = 'api/votes/parsers/'
}
