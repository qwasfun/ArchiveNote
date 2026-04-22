import { defineConfig, devices } from '@playwright/test'

/**
 * Playwright E2E 测试配置
 * 文档: https://playwright.dev/docs/test-configuration
 *
 * 运行前提：
 *   - 后端运行在 http://localhost:2601
 *   - 前端运行在 http://localhost:5173
 * 可通过 webServer 配置自动启动，也可手动预先启动。
 */
export default defineConfig({
  testDir: './e2e',
  timeout: 30_000,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI ? 'github' : 'list',

  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // 在 CI 中自动启动 Vite 开发服务器（后端需单独启动）
  webServer: process.env.CI
    ? {
        command: 'npm run dev',
        cwd: './web',
        url: 'http://localhost:5173',
        reuseExistingServer: false,
        timeout: 60_000,
      }
    : undefined,
})
