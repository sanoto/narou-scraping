import { Store } from 'vuex'
import { getModule } from 'vuex-module-decorators'
import { GeneralModule } from '~/store/general'
import { VotingModule } from '~/store/vote/voting'
import { VoteModule } from '~/store/vote/vote'
import { ParserModule } from '~/store/vote/parser'

/* eslint-disable import/no-mutable-exports */
let generalStore: GeneralModule
let votingStore: VotingModule
let voteStore: VoteModule
let parserStore: ParserModule
/* eslint-enable */

function initialiseStores(store: Store<any>): void {
  generalStore = getModule(GeneralModule, store)
  votingStore = getModule(VotingModule, store)
  voteStore = getModule(VoteModule, store)
  parserStore = getModule(ParserModule, store)
}

export { initialiseStores, generalStore, votingStore, voteStore, parserStore }
