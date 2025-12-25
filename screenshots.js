const { chromium } = require('playwright');

(async () => {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();

    console.log('📸 بدء التقاط صور للشاشة...\n');

    // Set viewport
    await page.setViewportSize({ width: 1920, height: 1080 });

    // 1. Home Page - Full Page
    console.log('📸 لقطة 1: الصفحة الرئيسية');
    await page.goto('http://localhost:5000/index', { waitUntil: 'networkidle' });
    await page.screenshot({ path: '/workspace/brilliox-unified/screenshot-1-homepage.png', fullPage: true });
    console.log('   ✅ تم حفظ: screenshot-1-homepage.png');

    // 2. Hero Section
    console.log('📸 لقطة 2: قسم الهيرو');
    await page.goto('http://localhost:5000/index', { waitUntil: 'networkidle' });
    await page.evaluate(() => window.scrollTo(0, 200));
    await page.screenshot({ path: '/workspace/brilliox-unified/screenshot-2-hero.png' });
    console.log('   ✅ تم حفظ: screenshot-2-hero.png');

    // 3. Features Section
    console.log('📸 لقطة 3: قسم المميزات');
    await page.goto('http://localhost:5000/index', { waitUntil: 'networkidle' });
    await page.evaluate(() => window.scrollTo(0, 800));
    await page.waitForTimeout(500);
    await page.screenshot({ path: '/workspace/brilliox-unified/screenshot-3-features.png' });
    console.log('   ✅ تم حفظ: screenshot-3-features.png');

    // 4. Chat Section
    console.log('📸 لقطة 4: قسم الدردشة');
    await page.goto('http://localhost:5000/index', { waitUntil: 'networkidle' });
    await page.evaluate(() => window.scrollTo(0, 1400));
    await page.waitForTimeout(500);
    await page.screenshot({ path: '/workspace/brilliox-unified/screenshot-4-chat.png' });
    console.log('   ✅ تم حفظ: screenshot-4-chat.png');

    // 5. Login Section
    console.log('📸 لقطة 5: قسم تسجيل الدخول');
    await page.goto('http://localhost:5000/index', { waitUntil: 'networkidle' });
    await page.evaluate(() => window.scrollTo(0, 2000));
    await page.waitForTimeout(500);
    await page.screenshot({ path: '/workspace/brilliox-unified/screenshot-5-login.png' });
    console.log('   ✅ تم حفظ: screenshot-5-login.png');

    // 6. Mobile View
    console.log('📸 لقطة 6: عرض الموبايل');
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto('http://localhost:5000/index', { waitUntil: 'networkidle' });
    await page.screenshot({ path: '/workspace/brilliox-unified/screenshot-6-mobile.png', fullPage: true });
    console.log('   ✅ تم حفظ: screenshot-6-mobile.png');

    // 7. API Health
    console.log('📸 لقطة 7: فحص API');
    await page.goto('http://localhost:5000/health', { waitUntil: 'networkidle' });
    await page.screenshot({ path: '/workspace/brilliox-unified/screenshot-7-api-health.png' });
    console.log('   ✅ تم حفظ: screenshot-7-api-health.png');

    // 8. API Documentation
    console.log('📸 لقطة 8: توثيق API');
    await page.goto('http://localhost:5000/docs', { waitUntil: 'networkidle' });
    await page.screenshot({ path: '/workspace/brilliox-unified/screenshot-8-api-docs.png', fullPage: true });
    console.log('   ✅ تم حفظ: screenshot-8-api-docs.png');

    console.log('\n✅ تم التقاط جميع الصور بنجاح!');
    console.log('📁 الموقع: /workspace/brilliox-unified/');

    await browser.close();
})();
