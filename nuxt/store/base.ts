import { mutation, action, Module, VuexModule } from 'vuex-class-component/dist'
import map from 'ramda/es/map'

import { $axios } from '@/utils/api'
import {
  appendToList,
  updateList,
  removeFromList,
  createModel,
  createParams,
} from '@/utils/ramda-ex'
import { Params, Model } from '@/store/django-types'
import { VoteStore } from '@/store/vote/vote'
import { VotingStore } from '@/store/vote/voting'
import { ParserStore } from '@/store/vote/parser'

export interface DjangoModule {
  data: Params[]
  pkName: string // = 'id'
  url: string // = 'api/hoge_app/hoge_model/'
  readonlyParams: string[] // = ['id']
}

export const enum StoreName {
  voting = 'voting',
  vote = 'vote',
  parser = 'parser',
}

@Module({ target: 'nuxt', namespacedPath: 'django' })
export class DjangoRestStore extends VuexModule {
  [StoreName.voting] = VotingStore.CreateSubModule(VotingStore);
  [StoreName.vote] = VoteStore.CreateSubModule(VoteStore);
  [StoreName.parser] = ParserStore.CreateSubModule(ParserStore)

  @mutation setData(params: { storeName: StoreName; data: Model[] }) {
    this[params.storeName].data = params.data
  }

  @mutation addInstance(params: { storeName: StoreName; instance: Model }) {
    this[params.storeName].data = appendToList(
      params.instance,
      this[params.storeName].data
    )
  }

  @mutation updateInstance(params: { storeName: StoreName; instance: Model }) {
    const pkName = this[params.storeName].pkName
    this[params.storeName].data = updateList(
      params.instance,
      pkName,
      this[params.storeName].data
    )
  }

  @mutation
  removeInstance(params: { storeName: StoreName; pk: string }) {
    const pkName = this[params.storeName].pkName
    this[params.storeName].data = removeFromList(
      params.pk,
      pkName,
      this[params.storeName].data
    )
  }

  @action
  async fetch(storeName: StoreName) {
    const result: Params[] = await $axios
      .$get(this[storeName].url)
      .then((response) => response.results)
      .catch((error) => {
        console.warn(error)
      })
    this.setData({
      storeName,
      data: map((a) => createModel(a, this[storeName].pkName), result),
    })
  }

  @action
  async add(params: { storeName: StoreName; instance: Model }) {
    const result: Params = await $axios
      .$post(
        this[params.storeName].url,
        createParams(params.instance, this[params.storeName].readonlyParams)
      )
      .then((response) => response)
      .catch((error) => {
        console.warn(error)
      })
    this.addInstance({
      storeName: params.storeName,
      instance: createModel(result, this[params.storeName].pkName),
    })
  }

  @action
  async update(params: {
    storeName: StoreName
    pk: string
    partialInstance: Params
  }) {
    const result: Params = await $axios
      .$patch(
        `${this[params.storeName].url}${params.pk}/`,
        createParams(
          params.partialInstance,
          this[params.storeName].readonlyParams
        )
      )
      .then((response) => response)
      .catch((error) => {
        console.warn(error)
      })
    this.updateInstance({
      storeName: params.storeName,
      instance: createModel(result, this[params.storeName].pkName),
    })
  }

  @action
  async delete(params: { storeName: StoreName; pk: string }) {
    await $axios
      .$delete(`${this[params.storeName].url}${params.pk}/`)
      .then((response) => response)
      .catch((error) => {
        console.warn(error)
      })
    this.removeInstance({ storeName: params.storeName, pk: params.pk })
  }
}
