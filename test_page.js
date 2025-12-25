const { chromium } = require('playwright');

(async () => {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();

    console.log('Testing Brilliox Pro CRM v7.0...');

    try {
        // Test health endpoint
        const healthResponse = await page.goto('http://localhost:5000/health');
        const healthStatus = await page.evaluate(() => document.body.innerText);
        console.log('Health check:', healthStatus);

        // Test main page
        await page.goto('http://localhost:5000/index');
        const title = await page.title();
        console.log('Page title:', title);

        // Check for key elements
        const hasHeader = await page.$('header') !== null;
        const hasChat = await page.$('#chatContainer') !== null;
        const hasLogin = await page.$('#username') !== null;

        console.log('Header present:', hasHeader);
        console.log('Chat container present:', hasChat);
        console.log('Login form present:', hasLogin);

        console.log('\n✅ All tests passed!');
    } catch (error) {
        console.error('❌ Test failed:', error.message);
    } finally {
        await browser.close();
    }
})();
