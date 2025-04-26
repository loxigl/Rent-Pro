/**
 * Скрипт для запуска Lighthouse тестов на страницах проекта.
 * Проверяет соответствие страниц требованиям производительности.
 */

const {exec} = require('child_process');
const fs = require('fs');
const path = require('path');

// URL для тестирования
const pages = [
    {
        name: 'home',
        url: 'http://localhost:3000/',
        thresholds: {performance: 90, accessibility: 90, seo: 95}
    },
    {
        name: 'catalog',
        url: 'http://localhost:3000/catalog',
        thresholds: {performance: 90, accessibility: 90, seo: 95}
    },
    {
        name: 'apartment-detail',
        url: 'http://localhost:3000/apartment/1', // Предполагается, что ID 1 существует
        thresholds: {performance: 90, accessibility: 90, seo: 95}
    }
];

// Директория для сохранения отчетов
const reportsDir = path.join(__dirname, '../lighthouse-reports');

// Создаем директорию, если она не существует
if (!fs.existsSync(reportsDir)) {
    fs.mkdirSync(reportsDir, {recursive: true});
}

/**
 * Запуск Lighthouse для указанной страницы
 */
function runLighthouse(page) {
    const outputPath = path.join(reportsDir, `${page.name}-report.html`);

    console.log(`\n🔍 Running Lighthouse for ${page.name} (${page.url})...`);

    const command = `npx lighthouse ${page.url} \
    --output=html \
    --output-path=${outputPath} \
    --preset=mobile \
    --quiet \
    --chrome-flags="--headless --no-sandbox --disable-gpu"`;

    return new Promise((resolve, reject) => {
        exec(command, (error, stdout, stderr) => {
            if (error) {
                console.error(`❌ Error running Lighthouse for ${page.name}:`, error);
                return reject(error);
            }

            console.log(`✅ Lighthouse report generated for ${page.name}`);
            console.log(`📊 Report saved to: ${outputPath}`);

            // Проверяем результаты на соответствие порогам
            try {
                const jsonOutputPath = outputPath.replace('.html', '.json');
                if (fs.existsSync(jsonOutputPath)) {
                    const report = JSON.parse(fs.readFileSync(jsonOutputPath, 'utf8'));

                    const scores = {
                        performance: Math.round(report.categories.performance.score * 100),
                        accessibility: Math.round(report.categories.accessibility.score * 100),
                        seo: Math.round(report.categories['best-practices'].score * 100),
                        bestPractices: Math.round(report.categories['seo'].score * 100)
                    };

                    console.log('📈 Scores:', JSON.stringify(scores, null, 2));

                    // Проверяем пороги
                    const thresholds = page.thresholds;
                    let failed = false;

                    if (scores.performance < thresholds.performance) {
                        console.error(`❌ Performance score (${scores.performance}) is below threshold (${thresholds.performance})`);
                        failed = true;
                    }

                    if (scores.accessibility < thresholds.accessibility) {
                        console.error(`❌ Accessibility score (${scores.accessibility}) is below threshold (${thresholds.accessibility})`);
                        failed = true;
                    }

                    if (scores.seo < thresholds.seo) {
                        console.error(`❌ SEO score (${scores.seo}) is below threshold (${thresholds.seo})`);
                        failed = true;
                    }

                    if (!failed) {
                        console.log('✅ All scores are above thresholds');
                    }

                    // Удаляем JSON-файл отчета
                    fs.unlinkSync(jsonOutputPath);
                }
            } catch (e) {
                console.error('Error parsing Lighthouse results:', e);
            }

            resolve();
        });
    });
}

/**
 * Запуск всех тестов последовательно
 */
async function runTests() {
    console.log('🚀 Starting Lighthouse tests...');

    for (const page of pages) {
        try {
            await runLighthouse(page);
        } catch (error) {
            console.error(`Failed to test ${page.name}:`, error);
        }
    }

    console.log('\n🏁 Lighthouse tests completed!');
}

// Запускаем тесты
runTests().catch(console.error);