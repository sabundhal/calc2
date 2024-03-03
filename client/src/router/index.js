import { createRouter, createWebHistory } from 'vue-router'
import Books from '../components/Books.vue'
import Register from '../components/Register.vue'
import Login from '../components/Login.vue'

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
  ]
})

export default router
