const { chromium } = require('playwright');

(async () => {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();

    console.log('🧪 بدء الاختبارات الشاملة لـ Brilliox Pro CRM v7.0');
    console.log('=' .repeat(60));

    const results = [];

    try {
        // 1. اختبار فحص الصحة
        console.log('\n📊 اختبار 1: فحص صحة النظام');
        const healthResponse = await page.goto('http://localhost:5000/health');
        const healthData = await page.evaluate(() => document.body.innerText);
        const healthJson = JSON.parse(healthData);
        console.log('   الحالة:', healthJson.status);
        console.log('   الإصدار:', healthJson.version);
        console.log('   قاعدة البيانات:', healthJson.database);
        results.push({ test: 'فحص الصحة', passed: healthJson.status === 'healthy' });

        // 2. اختبار الصفحة الرئيسية
        console.log('\n📊 اختبار 2: الصفحة الرئيسية');
        await page.goto('http://localhost:5000/index');
        const title = await page.title();
        console.log('   العنوان:', title);

        // التحقق من العناصر
        const header = await page.$('header');
        const hero = await page.$('section');
        const features = await page.$$('.glass.rounded-2xl');
        const chat = await page.$('#chatContainer');
        const login = await page.$('#login');
        const footer = await page.$('footer');

        console.log('   الهيدر:', header ? '✅ موجود' : '❌ غير موجود');
        console.log('   قسم Hero:', hero ? '✅ موجود' : '❌ غير موجود');
        console.log('   بطاقات المميزات:', features.length, 'بطاقات');
        console.log('   منطقة الدردشة:', chat ? '✅ موجودة' : '❌ غير موجودة');
        console.log('   نموذج تسجيل الدخول:', login ? '✅ موجود' : '❌ غير موجود');
        console.log('   التذييل:', footer ? '✅ موجود' : '❌ غير موجود');

        results.push({
            test: 'الصفحة الرئيسية',
            passed: header && hero && features.length >= 5 && chat && login && footer
        });

        // 3. اختبار API تسجيل الدخول
        console.log('\n📊 اختبار 3: API تسجيل الدخول');
        const loginResponse = await page.evaluate(async () => {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: 'test_user' })
            });
            return response.json();
        });
        console.log('   نجاح:', loginResponse.success);
        console.log('   معرف المستخدم:', loginResponse.user_id);
        console.log('   الرصيد:', loginResponse.wallet_balance);
        results.push({ test: 'تسجيل الدخول', passed: loginResponse.success === true });

        // 4. اختبار API إضافة عميل
        console.log('\n📊 اختبار 4: API إضافة عميل');
        const addLeadResponse = await page.evaluate(async () => {
            const response = await fetch('/api/leads/test_user/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: 'عميل اختبار',
                    phone: '0123456789',
                    email: 'test@example.com',
                    status: 'new'
                })
            });
            return response.json();
        });
        console.log('   نجاح:', addLeadResponse.success);
        console.log('   معرف العميل:', addLeadResponse.lead_id);
        results.push({ test: 'إضافة عميل', passed: addLeadResponse.success === true });

        // 5. اختبار API جلب العملاء
        console.log('\n📊 اختبار 5: API جلب العملاء');
        const leadsResponse = await page.evaluate(async () => {
            const response = await fetch('/api/leads/test_user');
            return response.json();
        });
        console.log('   عدد العملاء:', leadsResponse.count);
        console.log('   نجاح:', leadsResponse.leads ? '✅' : '❌');
        results.push({ test: 'جلب العملاء', passed: leadsResponse.leads && leadsResponse.count > 0 });

        // 6. اختبار API الإحصائيات
        console.log('\n📊 اختبار 6: API الإحصائيات');
        const statsResponse = await page.evaluate(async () => {
            const response = await fetch('/api/stats/test_user');
            return response.json();
        });
        console.log('   المستخدم:', statsResponse.user_id);
        console.log('   الرصيد:', statsResponse.wallet_balance);
        console.log('   إجمالي العملاء:', statsResponse.leads?.total);
        results.push({ test: 'الإحصائيات', passed: statsResponse.user_id === 'test_user' });

        // 7. اختبار API الترجمة
        console.log('\n📊 اختبار 7: API الترجمة');
        const translationsResponse = await page.evaluate(async () => {
            const response = await fetch('/api/translations/ar');
            return response.json();
        });
        console.log('   اللغة:', translationsResponse.lang);
        console.log('   الاتجاه:', translationsResponse.direction);
        console.log('   عدد الترجمات:', Object.keys(translationsResponse.translations || {}).length);
        results.push({ test: 'الترجمة', passed: translationsResponse.direction === 'rtl' });

        // 8. اختبار صفحة الويب (DOM)
        console.log('\n📊 اختبار 8: فحص عناصر الصفحة');
        const elements = await page.evaluate(() => {
            return {
                h1: document.querySelectorAll('h1').length,
                h2: document.querySelectorAll('h2').length,
                buttons: document.querySelectorAll('button').length,
                inputs: document.querySelectorAll('input').length,
                scripts: document.querySelectorAll('script').length,
                links: document.querySelectorAll('a').length
            };
        });
        console.log('   عناوين H1:', elements.h1);
        console.log('   عناوين H2:', elements.h2);
        console.log('   الأزرار:', elements.buttons);
        console.log('   حقول الإدخال:', elements.inputs);
        console.log('   السكريبتات:', elements.scripts);
        console.log('   الروابط:', elements.links);
        results.push({ test: 'فحص العناصر', passed: elements.h1 >= 1 && elements.buttons >= 3 });

        // 9. اختبار دعم PWA
        console.log('\n📊 اختبار 9: دعم PWA');
        const manifest = await page.evaluate(async () => {
            const response = await fetch('/static/manifest.json');
            return response.json();
        });
        console.log('   اسم التطبيق:', manifest.name);
        console.log('   الأيقونات:', manifest.icons?.length || 0);
        console.log('   الوضع:', manifest.display);
        results.push({ test: 'PWA Manifest', passed: manifest.name === 'Brilliox Pro CRM' });

        // 10. اختبار CSS والستايلات
        console.log('\n📊 اختبار 10: الستايلات والرسوم');
        const styles = await page.evaluate(() => {
            const glass = document.querySelector('.glass');
            const body = document.body;
            return {
                hasGlass: glass !== null,
                bodyBg: window.getComputedStyle(body).background,
                hasTailwind: Array.from(document.scripts).some(s => s.src.includes('tailwind'))
            };
        });
        console.log('   تأثير Glass:', styles.hasGlass ? '✅' : '❌');
        console.log('   Tailwind CSS:', styles.hasTailwind ? '✅' : '❌');
        results.push({ test: 'الرسوم', passed: styles.hasGlass && styles.hasTailwind });

        // ملخص النتائج
        console.log('\n' + '=' .repeat(60));
        console.log('📋 ملخص نتائج الاختبارات');
        console.log('=' .repeat(60));

        let passed = 0;
        let failed = 0;

        results.forEach((result, index) => {
            const status = result.passed ? '✅' : '❌';
            console.log(`${status} اختبار ${index + 1}: ${result.test}`);
            if (result.passed) passed++; else failed++;
        });

        console.log('\n' + '-'.repeat(60));
        console.log(`📊 المجموع: ${passed} نجح | ${failed} فشل من ${results.length} اختبار`);
        console.log('-'.repeat(60));

        if (failed === 0) {
            console.log('\n🎉 جميع الاختبارات نجحت! التطبيق يعمل بشكل مثالي.');
        } else {
            console.log('\n⚠️ بعض الاختبارات فشلت. راجع الأخطاء أعلاه.');
        }

    } catch (error) {
        console.error('\n❌ خطأ في الاختبارات:', error.message);
    } finally {
        await browser.close();
    }
})();
