import { createRouter, createWebHistory } from 'vue-router'

import IndexView from '@/views/index/IndexView.vue'
import HomeView from '@/views/index/HomeView.vue'

import LoginView from '@/views/auth/LoginView.vue'
import RegisterView from '@/views/auth/RegisterView.vue'

import NotesList from '@/views/notes/NotesList.vue'
import NotesDetail from '@/views/notes/NotesDetail.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'index', component: IndexView },
    { path: '/home', name: 'home', component: HomeView },
    { path: '/login', redirect: '/auth/login' },
    { path: '/auth/register', name: 'register', component: RegisterView },
    { path: '/auth/login', name: 'login', component: LoginView },
    { path: '/notes', name: 'notesList', component: NotesList },
    { path: '/notes/:id', name: 'notesDetail', component: NotesDetail },
  ],
})

export default router
