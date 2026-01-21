import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import Toast from './components/Toast.vue'

import './styles/style.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

// 注册全局组件
app.component('Toast', Toast)

app.mount('#app')
