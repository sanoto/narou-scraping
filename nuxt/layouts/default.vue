<template>
  <v-app dark>
    <v-navigation-drawer v-model="drawer" clipped fixed app>
      <v-list>
        <v-list-item
          v-for="item of navItems"
          :key="item.id"
          :to="item.to"
          router
          exact
        >
          <v-list-item-action>
            <v-icon>{{ item.icon }}</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title v-text="item.title" />
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-app-bar clipped-left fixed app>
      <v-app-bar-nav-icon @click.stop="drawer = !drawer" />
      <v-toolbar-title v-text="title" />
    </v-app-bar>

    <v-content>
      <v-container>
        <nuxt />
      </v-container>
    </v-content>
  </v-app>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'nuxt-property-decorator'
import { generalStore } from '~/store'

export interface NavItem {
  id: number
  icon: string
  title: string
  to: string
}

@Component
export default class VotingPage extends Vue {
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

  drawer: boolean = false

  get title() {
    return generalStore.title
  }
}
</script>
