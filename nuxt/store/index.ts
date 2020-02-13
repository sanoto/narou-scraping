import { Store } from 'vuex'

import { GeneralStore } from '~/store/general'
import { DjangoRestStore } from '~/store/base'
import { VotingStore } from '~/store/vote/voting'
import { VoteStore } from '~/store/vote/vote'
import { ParserStore } from '~/store/vote/parser'

export const store = new Store({
  modules: {
    general: GeneralStore.ExtractVuexModule(GeneralStore),
    django: DjangoRestStore.ExtractVuexModule(DjangoRestStore),
    voting: VotingStore.ExtractVuexModule(VotingStore),
    vote: VoteStore.ExtractVuexModule(VoteStore),
    parser: ParserStore.ExtractVuexModule(ParserStore),
  },
  strict: false,
})

export interface VXM {
  general: GeneralStore
  django: DjangoRestStore
  voting: VotingStore
  vote: VoteStore
  parser: ParserStore
}

export const vxm: VXM = {
  general: GeneralStore.CreateProxy(store, GeneralStore),
  django: DjangoRestStore.CreateProxy(store, DjangoRestStore),
  voting: VotingStore.CreateProxy(store, VotingStore),
  vote: VoteStore.CreateProxy(store, VoteStore),
  parser: ParserStore.CreateProxy(store, ParserStore),
}
