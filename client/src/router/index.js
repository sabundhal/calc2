import { createRouter, createWebHistory } from 'vue-router';
import Books from '../components/Books.vue';
import Register from '../components/Register.vue';
import Login from '../components/Login.vue';
import K8sLog from '../components/K8sLog.vue';
import Account from '../components/Account.vue';
import Main from '../components/Main.vue';
import Pediatric from '../components/Pediatric.vue';

const routes = [
  {
    path: '/',
    redirect: '/main'  // Перенаправляем с корневого пути на /main
  },
  {
    path: '/books',
    name: 'Books',
    component: Books,
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/main',
    name: 'Main',
    component: Main,
  },
  {
    path: '/k8sLog',
    name: 'K8sLog',
    component: K8sLog,
  },
  {
    path: '/account',
    name: 'Account',
    component: Account,
  },
  {
    path: '/pediatric',
    name: 'Pediatric',
    component: Pediatric,
    meta: { requiresAuth: true }  // Добавляем мета-поле для проверки авторизации
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL || '/'),  // Используем BASE_URL, если он есть
  routes
});

router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('access_token');  // Проверка наличия токена
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login');  // Перенаправляем на страницу логина, если пользователь не авторизован
  } else {
    next();  // Разрешаем переход
  }
});

export default router;