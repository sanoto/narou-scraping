import { VuexModule, Module, Mutation, Action } from 'vuex-module-decorators'
import { DateTime } from 'luxon'

import { BaseRestModule } from '~/store/base'

export interface Voting {
  name: string
  novel: number
  startTime: DateTime
  endTime: DateTime
  inImpression: boolean
  inWriterReport: boolean
  parsers: number[]
  participants: number[]
}

@Module({ stateFactory: true, namespaced: true, name: 'voting' })
export class VotingModule extends BaseRestModule<Voting, number> {
  url: string = 'api/votes/voting_list/'
}
