import { createRouter, createWebHistory } from 'vue-router'
import Books from '../components/Books.vue'
import Register from '../components/Register.vue'
import Login from '../components/Login.vue'
import K8sLog from '../components/K8sLog.vue'
import Account from '../components/Account.vue';
import Main from '../components/Main.vue';


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/books' 
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
      path: '/',
      redirect: '/main'
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
  ]
})

export default router
