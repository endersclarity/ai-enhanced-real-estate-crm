// MLS Integration Browser Test Script
// Tests the Quick Form Generator MLS functionality from user perspective

const puppeteer = require('puppeteer');

async function testMLSIntegration() {
    let browser;
    let page;
    
    try {
        console.log('🚀 Starting MLS Integration Browser Test...');
        
        // Launch browser
        browser = await puppeteer.launch({
            headless: false, // Show browser for debugging
            args: ['--no-sandbox', '--disable-setuid-sandbox'],
            defaultViewport: { width: 1280, height: 720 }
        });
        
        page = await browser.newPage();
        
        // Enable console logging from page
        page.on('console', msg => console.log('PAGE LOG:', msg.text()));
        page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
        
        const baseUrl = 'http://172.22.206.209:3001';
        
        console.log('📄 Testing Quick Form Generator page load...');
        
        // Navigate to Quick Form Generator
        await page.goto(`${baseUrl}/quick-forms`, { 
            waitUntil: 'networkidle2',
            timeout: 10000 
        });
        
        // Wait for page to fully load
        await page.waitForSelector('.form-option', { timeout: 5000 });
        console.log('✅ Quick Form Generator page loaded successfully');
        
        // Select a form type to enable the form
        console.log('🎯 Selecting Statewide Advisory form...');
        await page.click('[data-form="statewide_buyer_seller_advisory"]');
        await page.waitForSelector('#quickFormSection', { visible: true, timeout: 5000 });
        console.log('✅ Form section displayed');
        
        // Test MLS property search
        console.log('🔍 Testing MLS property search functionality...');
        
        // Click on property search field
        await page.click('#propertySearch');
        
        // Test search with real MLS ID from our data
        console.log('🏠 Searching for MLS ID: 223102263...');
        await page.type('#propertySearch', '223102263');
        
        // Wait for search results
        await new Promise(resolve => setTimeout(resolve, 1000)); // Allow debounce time
        await page.waitForSelector('#propertySearchResults .dropdown-item', { 
            visible: true, 
            timeout: 5000 
        });
        
        // Check if MLS results are displayed
        const mlsResults = await page.$$('#propertySearchResults .dropdown-item');
        console.log(`✅ Found ${mlsResults.length} property search results`);
        
        // Check for MLS badge
        const mlsBadge = await page.evaluate(() => {
            const badges = Array.from(document.querySelectorAll('#propertySearchResults .badge'));
            return badges.some(badge => badge.textContent.includes('MLS'));
        });
        if (mlsBadge) {
            console.log('✅ MLS badge displayed in results');
        }
        
        // Test clicking on an MLS result
        console.log('🎯 Selecting first MLS property...');
        const firstResult = await page.$('#propertySearchResults .dropdown-item');
        if (firstResult) {
            await firstResult.click();
            
            // Check if property is selected
            await page.waitForSelector('#selectedProperty', { visible: true, timeout: 3000 });
            console.log('✅ Property selected successfully');
            
            // Check if MLS ID is displayed
            const mlsIdDisplay = await page.$('#mlsIdDisplay');
            if (mlsIdDisplay) {
                const isVisible = await page.evaluate(el => el.style.display !== 'none', mlsIdDisplay);
                if (isVisible) {
                    const mlsId = await page.$eval('#selectedMlsId', el => el.textContent);
                    console.log(`✅ MLS ID displayed: ${mlsId}`);
                } else {
                    console.log('⚠️ MLS ID display is hidden');
                }
            }
        }
        
        // Test address search
        console.log('🔍 Testing address-based search...');
        await page.click('#propertySearch');
        await page.keyboard.down('Control');
        await page.keyboard.press('KeyA');
        await page.keyboard.up('Control');
        await page.type('#propertySearch', 'Grass Valley');
        
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Check for combined results
        await page.waitForSelector('#propertySearchResults .dropdown-item', { 
            visible: true, 
            timeout: 5000 
        });
        
        const addressResults = await page.$$('#propertySearchResults .dropdown-item');
        console.log(`✅ Address search returned ${addressResults.length} results`);
        
        // Check for section headers (CRM vs MLS)
        const crmHeader = await page.$('#propertySearchResults .dropdown-header');
        if (crmHeader) {
            console.log('✅ Section headers displayed for CRM/MLS separation');
        }
        
        // Test form autofill
        console.log('🚀 Testing autofill functionality...');
        await page.click('button[onclick="applyAutofillData()"]');
        
        // Wait for autofill to complete
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Check if property address was filled
        const propertyAddressField = await page.$('input[name="property_address"]');
        if (propertyAddressField) {
            const value = await page.evaluate(el => el.value, propertyAddressField);
            if (value.trim()) {
                console.log(`✅ Property address autofilled: ${value}`);
            } else {
                console.log('⚠️ Property address not autofilled');
            }
        }
        
        // Test API endpoints directly
        console.log('🔗 Testing MLS API endpoints...');
        
        // Test search endpoint
        const searchResponse = await page.evaluate(async () => {
            const response = await fetch('/api/mls/search?q=223102263');
            return await response.json();
        });
        
        if (searchResponse.success) {
            console.log(`✅ MLS search API working - found ${searchResponse.listings.length} listings`);
        } else {
            console.log('❌ MLS search API failed:', searchResponse.error);
        }
        
        // Test lookup endpoint
        const lookupResponse = await page.evaluate(async () => {
            const response = await fetch('/api/mls/lookup/223102263');
            return await response.json();
        });
        
        if (lookupResponse.success) {
            console.log('✅ MLS lookup API working');
            console.log(`   Address: ${lookupResponse.property.basic_info.address}`);
            console.log(`   Price: $${lookupResponse.property.pricing.list_price?.toLocaleString()}`);
        } else {
            console.log('❌ MLS lookup API failed:', lookupResponse.error);
        }
        
        console.log('🎉 MLS Integration Test Complete!');
        
        // Keep browser open for manual inspection
        console.log('🔍 Browser will remain open for manual inspection...');
        await new Promise(resolve => setTimeout(resolve, 30000)); // Keep open for 30 seconds
        
    } catch (error) {
        console.error('❌ Test Error:', error.message);
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

// Run the test
testMLSIntegration().catch(console.error);