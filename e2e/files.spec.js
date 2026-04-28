import { test, expect } from '@playwright/test'

const BASE = 'http://localhost:5173'

function uniqueUser() {
  return `e2e_files_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`
}

/** 注册并登录，返回已认证页面 */
async function loginAs(page, username, password = 'password123') {
  await page.goto(`${BASE}/auth/register`)
  await page.getByPlaceholder('请输入用户名').fill(username)
  await page.getByPlaceholder('请输入密码').first().fill(password)
  await page.getByPlaceholder('请确认密码').fill(password)
  await page.getByRole('button', { name: /注册/ }).click()
  await expect(page).toHaveURL(`${BASE}/`)
}

test.describe('文件列表页面', () => {
  test('登录后可访问文件页面', async ({ page }) => {
    await loginAs(page, uniqueUser())
    await page.goto(`${BASE}/files`)
    await expect(page).toHaveURL(`${BASE}/files`)
    // 页面加载完成后不应显示错误
    await expect(page.getByText(/500|服务器错误/)).not.toBeVisible()
  })

  test('文件页面存在上传入口', async ({ page }) => {
    await loginAs(page, uniqueUser())
    await page.goto(`${BASE}/files`)
    // 上传按钮或拖拽区域应可见
    const uploadElement = page
      .getByRole('button', { name: /上传/ })
      .or(page.getByText(/上传文件/))
      .or(page.getByText(/拖拽/))
    await expect(uploadElement.first()).toBeVisible({ timeout: 10_000 })
  })
})

test.describe('笔记列表页面', () => {
  test('登录后可访问笔记页面', async ({ page }) => {
    await loginAs(page, uniqueUser())
    await page.goto(`${BASE}/notes`)
    await expect(page).toHaveURL(`${BASE}/notes`)
    await expect(page.getByText(/500|服务器错误/)).not.toBeVisible()
  })
})
