<template>
  <v-app>
    <v-app-bar>
      <v-app-bar-title>Imagetorio</v-app-bar-title>
      <v-spacer></v-spacer>
      <v-btn variant="plain" to="/printer">Printer</v-btn>
      <v-icon>mdi-circle-small </v-icon>
      <v-btn variant="plain" to="/lamps">Lamps</v-btn>
      <v-spacer></v-spacer>
      <v-spacer></v-spacer>
    </v-app-bar>
    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>
