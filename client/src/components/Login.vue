<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-10">
        <h1>Вход</h1>
        <hr><br><br>
        <alert :message="message" v-if="showMessage"></alert>
        <form @submit.prevent="handleLoginSubmit">
          <div class="mb-3">
            <label for="loginEmail" class="form-label">Username:</label>
            <input
              type="email"
              class="form-control"
              id="loginEmail"
              v-model="loginForm.username"
              placeholder="Введите email">
          </div>
          <div class="mb-3">
            <label for="loginPassword" class="form-label">Пароль:</label>
            <input
              type="password"
              class="form-control"
              id="loginPassword"
              v-model="loginForm.password"
              placeholder="Введите пароль">
          </div>
          <div class="btn-group" role="group">
            <button
              type="submit"
              class="btn btn-primary btn-sm">
              Войти
            </button>
          </div>
          <p class="mt-3">Еще не зарегистрированы? <router-link to="/register">Зарегистрируйтесь</router-link></p>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import router from '@/router'; 
import Alert from './Alert.vue';
import config from '../config';

export default {
  data() {
    return {
      loginForm: {
        username: '',
        password: '',
      },
      message: '',
      showMessage: false,
    };
  },
  components: {
    alert: Alert,
  },
  methods: {
  loginUser(payload) {
    const path = `/api/login`;
    axios.post(path, payload)
      .then((response) => {
        const token = response.data.access_token; 
        localStorage.setItem('access_token', token); 
        localStorage.setItem('user_name', this.loginForm.username);
        localStorage.setItem('user_id', user_id);
        this.message = 'Вход выполнен успешно!';
        this.showMessage = true;
        this.resetForm();
        router.push({ name: 'Books' });
      })
      .catch((error) => {
        console.error(error);
        this.showMessage = false;
        this.message = 'Ошибка при входе. Проверьте правильность email и пароля.';
      });
  },
    handleLoginSubmit() {
      let payload = {
        username: this.loginForm.username,
        password: this.loginForm.password,
      };
      this.loginUser(payload);
    },
    resetForm() {
      this.loginForm.username = '';
      this.loginForm.password = '';
    },
  },
    beforeRouteEnter(to, from, next) {
    const token = localStorage.getItem('access_token');
    if (token) {
      router.push({ name: 'Books' }); 
    } else {
      next(); 
    }
  },
};
</script>
