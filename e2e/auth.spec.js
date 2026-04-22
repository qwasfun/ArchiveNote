import { test, expect } from '@playwright/test'

const BASE = 'http://localhost:5173'

// 每次测试使用唯一用户名，避免注册冲突
function uniqueUser() {
  return `e2e_user_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`
}

test.describe('注册与登录', () => {
  test('注册新用户并自动跳转到首页', async ({ page }) => {
    const username = uniqueUser()
    await page.goto(`${BASE}/auth/register`)

    await page.getByPlaceholder('请输入用户名').fill(username)
    await page.getByPlaceholder('请输入密码').first().fill('password123')
    await page.getByPlaceholder('请确认密码').fill('password123')
    await page.getByRole('button', { name: /注册/ }).click()

    // 注册成功后跳转到首页
    await expect(page).toHaveURL(`${BASE}/`)
  })

  test('登录已存在用户', async ({ page }) => {
    const username = uniqueUser()

    // 先注册
    await page.goto(`${BASE}/auth/register`)
    await page.getByPlaceholder('请输入用户名').fill(username)
    await page.getByPlaceholder('请输入密码').first().fill('password123')
    await page.getByPlaceholder('请确认密码').fill('password123')
    await page.getByRole('button', { name: /注册/ }).click()
    await expect(page).toHaveURL(`${BASE}/`)

    // 登出（如果有登出按钮）
    const logoutBtn = page.getByRole('button', { name: /登出|退出/ })
    if (await logoutBtn.isVisible()) {
      await logoutBtn.click()
    } else {
      // 手动清除 localStorage 中的 token
      await page.evaluate(() => localStorage.clear())
      await page.goto(`${BASE}/auth/login`)
    }

    // 登录
    await page.goto(`${BASE}/auth/login`)
    await page.getByPlaceholder('请输入用户名').fill(username)
    await page.getByPlaceholder('请输入密码').fill('password123')
    await page.getByRole('button', { name: /登录/ }).click()

    await expect(page).toHaveURL(`${BASE}/`)
  })

  test('错误密码登录显示错误提示', async ({ page }) => {
    await page.goto(`${BASE}/auth/login`)
    await page.getByPlaceholder('请输入用户名').fill('nonexistent_user_xyz')
    await page.getByPlaceholder('请输入密码').fill('wrongpassword')
    await page.getByRole('button', { name: /登录/ }).click()

    // 页面应停留在登录页并显示错误信息
    await expect(page).toHaveURL(`${BASE}/auth/login`)
    await expect(page.getByText(/失败|错误|不正确|密码/)).toBeVisible({ timeout: 5000 })
  })

  test('未登录访问 /files 重定向到登录页', async ({ page }) => {
    await page.evaluate(() => localStorage.clear())
    await page.goto(`${BASE}/files`)
    await expect(page).toHaveURL(/auth\/login/)
  })
})
