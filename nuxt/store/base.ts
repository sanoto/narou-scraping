import { VuexModule, Module, Mutation, Action } from 'vuex-module-decorators'
import { renameKeysWith } from 'ramda-adjunct'
import camelCase from 'lodash/camelCase'
import snakeCase from 'lodash/snakeCase'
import omit from 'ramda/es/omit'
import merge from 'ramda/es/merge'
import assoc from 'ramda/es/assoc'
import map from 'ramda/es/map'
import prop from 'ramda/es/prop'
import fromPairs from 'ramda/es/fromPairs'

import { $axios } from '~/utils/api'

export type Params = { [key: string]: any }

// TODO: 継承が使えないのでここをMutateとActionのターミナルにする
// TODO: 対象の子モジュールに対象のAction/Mutateがなかったら共通のものを使用する
export abstract class BaseRestModule<
  Model extends Params,
  PK extends keyof any
> extends VuexModule {
  data = <Record<PK, Model>>{}
  pkName: string = 'id'
  url: string = 'api/'
  readonlyParams: string[] = ['id']

  @Mutation
  setData(data: Record<PK, Model>) {
    this.data = data
  }

  @Mutation
  updateData(data: Record<PK, Model>) {
    this.setData(merge(this.data, data))
  }

  @Mutation
  setInstance(pk: PK, instance: Model) {
    this.setData(assoc(pk, instance, this.data))
  }

  @Mutation
  removeInstance(pk: PK) {
    this.setData(<Record<PK, Model>>omit([pk], this.data))
  }

  createModel(resultParams: Params): [PK, Model] {
    const pk: PK = prop(this.pkName, resultParams)
    const idRemoved: Params = omit([this.pkName], resultParams)
    const instance = <Model>renameKeysWith(camelCase, idRemoved)
    return [pk, instance]
  }

  createParams(instance: Model | Params): Params {
    const snakeParams = renameKeysWith(snakeCase, instance)
    return omit(this.readonlyParams, snakeParams)
  }

  @Action
  async fetch() {
    const result: Params[] = await $axios
      .$get(this.url)
      .then((response) => response.data.results)
      .catch((error) => {
        console.warn(error)
      })
    this.setData(<Record<PK, Model>>fromPairs(map(this.createModel, result)))
  }

  @Action
  async add(instance: Model) {
    const result: Params = await $axios
      .$post(this.url, this.createParams(instance))
      .then((response) => response.data)
      .catch((error) => {
        console.warn(error)
      })
    this.setInstance(...this.createModel(result))
  }

  @Action
  async update(pk: PK, partialInstance: Params) {
    const result: Params = await $axios
      .$patch(`${this.url}${pk}/`, this.createParams(partialInstance))
      .then((response) => response.data)
      .catch((error) => {
        console.warn(error)
      })
    this.setInstance(...this.createModel(result))
  }

  @Action
  async delete(pk: PK) {
    await $axios
      .$delete(`${this.url}${pk}/`)
      .then((response) => response.data)
      .catch((error) => {
        console.warn(error)
      })
    this.removeInstance(pk)
  }
}
