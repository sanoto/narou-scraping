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
            v-for="voting in votingList"
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

<script>
import { mapState, mapActions } from 'vuex'

export default {
  async fetch({ store }) {
    // `fetch` メソッドはページの描画前にストアを満たすために使用されます
    await store.dispatch('vote/getValues', 'votingList')
  },
  computed: {
    ...mapState('vote', ['parsers', 'votingList', 'votes', 'writerDetail']),
    ...mapActions('vote', [
      'getValues',
      'addValue',
      'updateValue',
      'deleteValue'
    ])
  }
}
</script>

<style scoped></style>
