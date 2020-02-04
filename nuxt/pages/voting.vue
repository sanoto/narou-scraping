<template>
  <v-layout>
    <v-container fluid>
      <v-card>
        <v-card-title class="headline">
          投票集計ページ
        </v-card-title>
        <v-card-text>
          <p>{{ votingList[0].name }}</p>
        </v-card-text>
        <v-list>
          <v-list-item
            v-for="(voting, id) of votingList"
            :key="id"
            :to="id"
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
import { Component, Prop, Vue } from 'nuxt-property-decorator'
import { votingStore } from '~/store'

@Component
export default class VotingPage extends Vue {
  async fetch() {
    await votingStore.fetch()
  }

  get votingList() {
    return votingStore.data
  }
}
</script>

<style scoped></style>
