<template>
    <v-app-bar app>
      <v-spacer></v-spacer>
      <v-btn text to="/main">Главная</v-btn>
      <v-btn text to="/k8sLog">Логи Кубера</v-btn>
      <v-btn text to="/account">Счета</v-btn>
      <v-spacer></v-spacer>
    </v-app-bar>
  </template>

  <script>
  export default {
    name: "Menu",
  };
  </script>