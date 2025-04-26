import { defineConfig, devices } from '@playwright/test';

/**
 * Конфигурация для E2E тестов с Playwright.
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './tests',
  /* Максимальное время прохождения всех тестов */
  timeout: 30 * 1000,
  /* Ожидаем, что тесты выполняются в указанном порядке */
  expect: {
    /**
     * Максимальное время ожидания для проверок:
     * например, ожидание появления элемента
     */
    timeout: 5000
  },
  /* Число повторов упавших тестов */
  retries: process.env.CI ? 2 : 0,
  /* Параллельное выполнение тестов */
  workers: process.env.CI ? 1 : undefined,
  /* Репортеры для вывода результатов */
  reporter: [
    ['html', { open: 'never' }],
    ['list']
  ],
  /* Настройка собранного приложения для тестов */
  webServer: {
    command: 'npm run start',
    port: 3000,
    reuseExistingServer: !process.env.CI,
  },
  /* Общие для всех тестов настройки */
  use: {
    /* Базовый URL тестируемого приложения */
    baseURL: 'http://localhost:3000',

    /* Сбор трассировки во время тестов */
    trace: 'on-first-retry',

    /* Собирать видео при провале тестов */
    video: 'on-first-retry',

    /* Делать скриншоты при провале тестов */
    screenshot: 'only-on-failure',
  },

  /* Разные конфигурации устройств для тестирования */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'mobile',
      use: { ...devices['Pixel 5'] },
    },
  ],
});