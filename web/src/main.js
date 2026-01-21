import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import ToastMessage from './components/ToastMessage.vue'

import './styles/style.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

// 注册全局组件
app.component('ToastMessage', ToastMessage)

app.mount('#app')
