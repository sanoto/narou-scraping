import { Module, VuexModule } from 'vuex-class-component/dist'

import { DjangoModule } from '~/store/base'
import { Vote } from '~/store/django-types'

@Module({ target: 'nuxt', namespacedPath: 'vote' })
export class VoteStore extends VuexModule implements DjangoModule {
  data: Vote[] = []
  pkName: string = 'id'
  url: string = 'api/votes/votes/'
  readonlyParams: string[] = ['id']
}
