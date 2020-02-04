import { VuexModule, Module, Mutation, Action } from 'vuex-module-decorators'
import { DateTime } from 'luxon'

import { BaseRestModule } from '~/store/base'

export interface Vote {
  voting: number
  participant: number
  postedAt: DateTime
  content: string
}

@Module({ stateFactory: true, namespaced: true, name: 'vote' })
export class VoteModule extends BaseRestModule<Vote, number> {
  url: string = 'api/votes/votes/'
}
