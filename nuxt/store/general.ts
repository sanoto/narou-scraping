import { mutation, action, Module, VuexModule } from 'vuex-class-component/dist'

export interface NavItem {
  id: number
  icon: string
  title: string
  to: string
}

@Module({ target: 'nuxt', namespacedPath: 'general' })
export class GeneralStore extends VuexModule {
  title: string = 'なろう系サイト(α版)'
  navItems: NavItem[] = [
    {
      id: 1,
      icon: 'mdi-apps',
      title: 'トップ',
      to: '/',
    },
    {
      id: 2,
      icon: 'mdi-chart-bubble',
      title: '人気投票集計',
      to: '/voting',
    },
  ]

  @mutation setTitle(title: string) {
    this.title = title
  }
}
