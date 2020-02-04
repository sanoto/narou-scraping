import { VuexModule, Module, Mutation, Action } from 'vuex-module-decorators'

@Module({ stateFactory: true, namespaced: true, name: 'general' })
export class GeneralModule extends VuexModule {
  title: string = 'なろう系サイト'

  @Mutation
  setTitle(title: string) {
    this.title = title
  }
}
