import append from 'ramda/es/append'
import findIndex from 'ramda/es/findIndex'
import propEq from 'ramda/es/propEq'
import update from 'ramda/es/update'
import remove from 'ramda/es/remove'
import assoc from 'ramda/es/assoc'
import omit from 'ramda/es/omit'
import { renameKeysWith } from 'ramda-adjunct'
import camelCase from 'lodash/camelCase'
import snakeCase from 'lodash/snakeCase'

import { Model, Params } from '~/store/django-types'

export const appendToList = (obj: Params, list: Params[]): Model[] =>
  <Model[]>append(obj, list)

export const getObjIndex = (
  obj: Params,
  pkName: keyof Params,
  list: Params[]
): number => findIndex(propEq(pkName, obj[pkName]), list)

export const getPKIndex = (
  pk: string,
  pkName: keyof Params,
  list: Params[]
): number => findIndex(propEq(pkName, pk), list)

export function updateList(
  obj: Params,
  pkName: keyof Params,
  list: Params[]
): Model[] {
  const index = getObjIndex(obj, pkName, list)
  return <Model[]>(index === -1 ? list : update(index, obj, list))
}

export function removeFromList(
  pk: string,
  pkName: keyof Params,
  list: Params[]
): Model[] {
  const index = getPKIndex(pk, pkName, list)
  return <Model[]>(index === -1 ? list : remove(index, 1, list))
}

export function createModel(resultParams: Params, pkName: keyof Params): Model {
  const renamed: Params = renameKeysWith(camelCase, resultParams)
  return <Model>assoc(pkName, renamed[pkName].toString(), renamed)
}

export const createParams = (
  instance: Params,
  readonlyParams: string[]
): Params => omit(readonlyParams, renameKeysWith(snakeCase, instance))
