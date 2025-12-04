<template>
  <div class="pt-20">
    <fieldset class="fieldset mx-auto bg-base-200 border-base-300 rounded-box w-xs border p-4">
      <legend class="fieldset-legend">Register</legend>

      <label class="label">username</label>
      <input type="username" class="input" placeholder="username" />

      <label class="label">Password</label>
      <input type="password" class="input" placeholder="Password" />

      <button class="btn btn-neutral mt-4">Register</button>
      <div class="text-center pt-2">
        <RouterLink class="link link-primary" to="/auth/login">Login</RouterLink>
      </div>
    </fieldset>
  </div>
</template>
