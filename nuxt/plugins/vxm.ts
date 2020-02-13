import { Plugin } from '@nuxt/types'

import { vxm, VXM } from '@/store'

declare module 'vue/types/vue' {
  interface Vue {
    $vxm: VXM
  }
}

declare module '@nuxt/types' {
  interface NuxtAppOptions {
    $vxm: VXM
  }
}

declare module 'vuex/types/index' {
  interface Store<S> {
    $vxm: VXM
  }
}

const vxmPlugin: Plugin = (context, inject) => {
  inject('vxm', vxm)
}

export default vxmPlugin
