<template>
  <v-layout>
    <v-container fluid>
      <v-card>
        <v-card-title class="headline">
          投票集計ページ
        </v-card-title>
        <v-card-text>
          <p>{{ $vxm.voting.data[0].name }}</p>
        </v-card-text>
        <v-list>
          <v-list-item
            v-for="voting of $vxm.voting.data"
            :key="voting.id"
            :to="voting.id"
            router
            exact
          >
            <v-list-item-content>
              <v-list-item-title v-text="voting.name" />
            </v-list-item-content>
            <v-list-item-action>
              <v-btn icon>
                <v-icon>mdi-plus</v-icon>
              </v-btn>
            </v-list-item-action>
          </v-list-item>
        </v-list>
        <v-card-actions>
          <v-spacer />
          <v-btn color="primary" nuxt to="/inspire">
            Continue
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-container>
  </v-layout>
</template>

<script lang="ts">
import { Context } from '@nuxt/types'
import { Component, Vue } from 'nuxt-property-decorator'

import { StoreName } from '@/store/base'

@Component({
  async fetch({ app }: Context) {
    await app.$vxm.django.fetch(StoreName.voting)
  },
})
export default class VotingPage extends Vue {}
</script>

<style scoped></style>
