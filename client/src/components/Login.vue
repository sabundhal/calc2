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

        <!-- Кнопка для авторизации через Яндекс -->
        <div class="mt-4">
          <button class="btn btn-secondary btn-sm" @click="startYandexAuth">Войти через Яндекс</button>
        </div>
        <!-- Контейнер для кнопки SDK -->
    <div id="buttonContainerId"></div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import router from '@/router';

export default {
  data() {
    return {
      yandexAuthInProgress: false,
      loginForm: {
        username: '',
        password: '',
      },
      message: '',
      showMessage: false,
    };
  },

  methods: {
    startYandexAuth() {
      console.log('Кнопка "Войти через Яндекс" нажата');
      if (this.yandexAuthInProgress) {
        console.warn('Авторизация уже в процессе.');
        return;
      }
      this.yandexAuthInProgress = true;

      const script = document.createElement('script');
      script.src = 'https://yastatic.net/s3/passport-sdk/autofill/v1/sdk-suggest-with-polyfills-latest.js';
      script.onload = () => {
        console.log('SDK Яндекса успешно загружен');

        window.YaAuthSuggest.init(
          {
            client_id: 'e5b8dfc63c3c47f4965c09159fdd779c', // Ваш client_id
            response_type: 'token',
            redirect_uri: 'http://localhost:8080/tokenhandler', // Ваш redirect_uri
          },
          'http://localhost:8080', // Ваш origin
          {
            view: 'button',
            parentId: 'buttonContainerId',
            buttonSize: 'm',
            buttonView: 'main',
            buttonTheme: 'light',
            buttonBorderRadius: '0',
            buttonIcon: 'ya',
          }
        )
          .then(({ handler }) => {
            console.log('Инициализация SDK Яндекс успешна');
            return handler();
          })
          .then(data => {
            console.log('Данные после авторизации:', data);
            if (!data || !data.access_token) {
              throw new Error('Токен не получен.');
            }
            console.log('Токен получен:', data.access_token);
            this.sendTokenToServer(data.access_token);
          })
          .catch(error => {
            console.error('Ошибка авторизации:', error);
            alert(`Ошибка при входе через Яндекс: ${error.message}`);
          })
          .finally(() => {
            this.yandexAuthInProgress = false;
          });
      };
      script.onerror = () => {
        console.error('Ошибка при загрузке SDK Яндекса.');
        alert('Ошибка при загрузке модуля авторизации. Попробуйте снова.');
        this.yandexAuthInProgress = false;
      };
      document.head.appendChild(script);
    },

    sendTokenToServer(token) {
  axios.post('/api/auth/yandex', { token: token })
    .then(response => {
      console.log('Ответ от бекенда:', response.data);

      // Сохраняем токен и данные пользователя в localStorage
      localStorage.setItem('access_token', response.data.user.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));

      // Закрываем окно только после успешного завершения
      if (window.opener) {
        window.opener.postMessage({ type: 'yandexAuthSuccess', token: response.data.user.access_token }, '*');
        window.close();
      } else {
        this.$router.push({ name: 'Main' });
      }
    })
    .catch(error => {
      console.error('Ошибка при отправке токена:', error);
      alert('Ошибка при входе через Яндекс. Попробуйте снова.');
    });
},

    handleLoginSubmit() {
      const payload = {
        username: this.loginForm.username,
        password: this.loginForm.password,
      };
      this.loginUser(payload);
    },

    loginUser(payload) {
      const path = `/api/login`;
      axios.post(path, payload)
        .then((response) => {
          const token = response.data.access_token;
          const user_id = response.data.user_id;
          localStorage.setItem('access_token', token);
          localStorage.setItem('user_name', this.loginForm.username);
          localStorage.setItem('user_id', user_id);
          this.message = 'Вход выполнен успешно!';
          this.showMessage = true;
          this.resetForm();
          this.$router.push({ name: 'Books' });
        })
        .catch((error) => {
          console.error(error);
          this.showMessage = false;
          this.message = 'Ошибка при входе. Проверьте правильность email и пароля.';
        });
    },

    resetForm() {
      this.loginForm.username = '';
      this.loginForm.password = '';
    },

    handleMessage(event) {
      if (event.data.type === 'yandexAuthSuccess') {
        const token = event.data.token;
        console.log('Токен получен во всплывающем окне:', token);
        // Сохраняем токен и перенаправляем пользователя
        localStorage.setItem('access_token', token);
          // Вызываем sendTokenToServer в основном окне
      this.sendTokenToServer(token);
        this.$router.push({ name: 'Books' });
      }
    },
  },

  mounted() {
    window.addEventListener('message', this.handleMessage);
  },

  beforeDestroy() {
    window.removeEventListener('message', this.handleMessage);
  },

  beforeRouteEnter(to, from, next) {
  const token = localStorage.getItem('access_token');
  const user = localStorage.getItem('user');

  console.log('Токен в localStorage:', token);
  console.log('Данные пользователя в localStorage:', user);

  // Исключение для страницы логина
  if (to.name === 'Login') {
    console.log('Переход на страницу логина');
    next();
  } else if (user && to.name !== 'Main') {
    console.log('Перенаправление на /Main');
    next({ name: 'Main' });
  } else {
    console.log('Переход на текущий маршрут');
    next();
  }
},
};
</script>