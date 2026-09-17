import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import { i18n } from './i18n'
import router from './router' // <-- Добавили роутер

const app = createApp(App)
app.use(i18n)
app.use(router) // <-- Инициализировали роутер
app.mount('#app')
