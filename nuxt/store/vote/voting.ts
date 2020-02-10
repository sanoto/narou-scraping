import { Module, VuexModule } from 'vuex-class-component'

import { DjangoModule } from '~/store/base'
import { Voting } from '~/store/django-types'

@Module({ target: 'nuxt', namespacedPath: 'voting' })
export class VotingStore extends VuexModule implements DjangoModule {
  data: Voting[] = []
  pkName: string = 'id'
  url: string = 'api/votes/voting_list/'
  readonlyParams: string[] = ['id']
}
