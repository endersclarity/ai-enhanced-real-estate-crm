const puppeteer = require('puppeteer');

async function testMLSDisplay() {
    let browser;
    try {
        console.log('🚀 Starting Puppeteer browser...');
        browser = await puppeteer.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });
        
        const page = await browser.newPage();
        
        // Enable console logging from the page
        page.on('console', msg => {
            console.log('BROWSER CONSOLE:', msg.text());
        });
        
        page.on('pageerror', error => {
            console.error('PAGE ERROR:', error.message);
        });
        
        console.log('📊 Skipping debug page (404), going directly to Quick Form Generator...');
        
        console.log('📊 Testing Quick Form Generator...');
        await page.goto('http://172.22.206.209:3001/quick-forms', { 
            waitUntil: 'networkidle0',
            timeout: 10000 
        });
        
        // Find the property search input
        const propertyInput = await page.$('#propertySearch');
        if (propertyInput) {
            console.log('🔍 Found property search input');
            
            // Type Nevada City and trigger search manually
            await page.type('#propertySearch', 'nevada city');
            console.log('⌨️ Typed "nevada city"');
            
            // Wait a bit and then check if any network requests were made
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // Debug what happens when we manually trigger the search
            const debugInfo = await page.evaluate(() => {
                console.log('🔄 Calling searchProperties with "grass valley"...');
                searchProperties('grass valley');
                return { success: true, message: 'searchProperties called' };
            });
            
            console.log('🔍 Debug result:', debugInfo);
            
            // Wait for search results
            await new Promise(resolve => setTimeout(resolve, 3000));
            
            // Check if results div is visible
            const resultsDiv = await page.$('#propertySearchResults');
            const isVisible = await page.evaluate(el => {
                const style = window.getComputedStyle(el);
                return style.display !== 'none' && style.visibility !== 'hidden';
            }, resultsDiv);
            
            console.log('📊 Results div visible:', isVisible ? 'YES' : 'NO');
            
            // Get the inner HTML of results
            const resultsHTML = await page.$eval('#propertySearchResults', el => el.innerHTML);
            console.log('📋 Results HTML length:', resultsHTML.length);
            console.log('📋 Results HTML preview:', resultsHTML.substring(0, 300));
            
            // Check for MLS properties specifically
            const mlsItems = await page.$$('#propertySearchResults .dropdown-item');
            console.log('🏠 Number of property items found:', mlsItems.length);
            
        } else {
            console.log('❌ Property search input not found');
        }
        
    } catch (error) {
        console.error('❌ Error during testing:', error.message);
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

testMLSDisplay();