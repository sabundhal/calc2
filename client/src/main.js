import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import vuetify from './plugins/vuetify';
import { loadFonts } from './plugins/webfontloader';
import 'bootstrap/dist/css/bootstrap.css';

// Загружаем шрифты
loadFonts();

// Создаем приложение
const app = createApp(App);

// Подключаем плагины
app.use(router);
app.use(vuetify);

// Монтируем приложение
app.mount('#app');


