import { Module, VuexModule } from 'vuex-class-component/dist'

import { DjangoModule } from '~/store/base'
import { Parser } from '~/store/django-types'

@Module({ target: 'nuxt', namespacedPath: 'parser' })
export class ParserStore extends VuexModule implements DjangoModule {
  data: Parser[] = []
  pkName: string = 'id'
  url: string = 'api/votes/parsers/'
  readonlyParams: string[] = ['id']
}
