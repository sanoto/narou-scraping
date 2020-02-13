import { DateTime } from 'luxon'

export type Params = { [key: string]: any }
export type Model = Voting & Vote & Parser

export interface Voting extends Params {
  id: string
  name: string
  novel: number
  startTime: DateTime
  endTime: DateTime
  inImpression: boolean
  inWriterReport: boolean
  parsers: number[]
  participants: number[]
}

export interface Vote extends Params {
  id: string
  voting: number
  participant: number
  postedAt: DateTime
  content: string
}

export interface Parser extends Params {
  id: string
  regex: string
}
