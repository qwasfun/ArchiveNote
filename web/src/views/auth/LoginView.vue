<script setup>
import { ref } from 'vue'
import { login as loginApi } from '@/api/authService'
import router from '@/router'

const form = ref({})

const submit = function () {
  const params = {
    username: form.value.username,
    password: form.value.password,
  }
  loginApi(params)
    .then((res) => {
      const { user = {}, access_token, refresh_token } = res
      localStorage.setItem('user', JSON.stringify(user))
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)

      router.push('/')
    })
    .catch(() => {})
}
</script>

<template>
  <div class="pt-20">
    <fieldset class="fieldset mx-auto bg-base-200 border-base-300 rounded-box w-xs border p-4">
      <legend class="fieldset-legend">Login</legend>

      <label class="label">username</label>
      <input v-model="form.username" type="text" class="input" placeholder="username" />

      <label class="label">Password</label>
      <input v-model="form.password" type="password" class="input" placeholder="Password" />

      <button class="btn btn-neutral mt-4" @click="submit">Login</button>
      <div class="text-center pt-2">
        <RouterLink class="link link-primary" to="/auth/register">Register</RouterLink>
      </div>
    </fieldset>
  </div>
</template>
