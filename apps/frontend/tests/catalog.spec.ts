import { test, expect } from '@playwright/test';

/**
 * E2E тесты для страницы каталога и деталей квартиры
 */
test.describe('Каталог квартир', () => {
  // Перед каждым тестом открываем страницу каталога
  test.beforeEach(async ({ page }) => {
    await page.goto('/catalog');
  });

  // Тест загрузки каталога
  test('должен успешно загрузить страницу каталога', async ({ page }) => {
    // Проверяем заголовок страницы
    await expect(page).toHaveTitle(/Каталог квартир/);

    // Проверяем, что загружен текст заголовка
    await expect(page.locator('h1')).toHaveText('Каталог квартир');

    // Проверяем, что загружены карточки квартир
    await expect(page.locator('.card')).toHaveCount({ min: 1 });
  });

  // Тест пагинации
  test('должен работать с пагинацией', async ({ page }) => {
    // Проверяем наличие пагинации (если есть достаточно карточек)
    const pagination = page.locator('a[href*="page="]');

    // Если пагинация есть, проверяем переход на вторую страницу
    if (await pagination.count() > 0) {
      // Нажимаем на ссылку "Далее" или на номер страницы "2"
      await page.locator('a[href*="page=2"]').first().click();

      // Проверяем, что URL обновился
      await expect(page).toHaveURL(/page=2/);

      // Проверяем, что загружены карточки
      await expect(page.locator('.card')).toHaveCount({ min: 1 });
    }
  });

  // Тест сортировки
  test('должен корректно работать с сортировкой', async ({ page }) => {
    // Нажимаем на ссылку "Сначала дешевые"
    await page.locator('a[href*="sort=price_rub&order=asc"]').click();

    // Проверяем, что URL обновился
    await expect(page).toHaveURL(/sort=price_rub&order=asc/);

    // Проверяем, что загрузились карточки
    await expect(page.locator('.card')).toHaveCount({ min: 1 });
  });

  // Тест открытия детальной страницы
  test('должен открывать детальную страницу при клике на карточку', async ({ page }) => {
    // Ожидаем загрузку карточек
    await page.waitForSelector('.card');

    // Сохраняем URL первой карточки для проверки редиректа
    const cardLink = await page.locator('.card').first().getAttribute('href');

    // Кликаем по первой карточке
    await page.locator('.card').first().click();

    // Проверяем, что перешли на страницу с правильным URL
    await expect(page).toHaveURL(cardLink || '/apartment/');

    // Ожидаем загрузку галереи
    await page.waitForSelector('.apartment-gallery');

    // Проверяем, что загрузились ключевые элементы детальной страницы
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('.apartment-gallery')).toBeVisible();
  });
});

/**
 * Тест для детальной страницы квартиры
 */
test.describe('Детальная страница квартиры', () => {
  // Тест загрузки деталей квартиры и функциональности
  test('должна корректно отображать информацию и функциональность', async ({ page }) => {
    // Сначала открываем каталог
    await page.goto('/catalog');

    // Ожидаем загрузку карточек
    await page.waitForSelector('.card');

    // Кликаем по первой карточке
    await page.locator('.card').first().click();

    // Проверяем, что загрузились основные элементы
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('.apartment-gallery')).toBeVisible();

    // Проверяем наличие кнопок связи
    await expect(page.locator('a[href^="tel:"]')).toBeVisible();

    // Проверяем наличие характеристик
    await expect(page.locator('text=Характеристики')).toBeVisible();

    // Проверяем наличие описания
    await expect(page.locator('text=Описание')).toBeVisible();

    // Проверяем работу навигации (возврат в каталог)
    await page.locator('a[href="/catalog"]').click();
    await expect(page).toHaveURL('/catalog');
  });
});