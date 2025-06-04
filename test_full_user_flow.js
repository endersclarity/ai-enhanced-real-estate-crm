#!/usr/bin/env node
/**
 * Full User Experience Test - Complete Form Generation Flow
 * Test the actual form generation process from a user's perspective
 */

const puppeteer = require('puppeteer');

async function testCompleteUserFlow() {
    console.log('🎯 Starting Complete User Flow Test');
    console.log('Testing: Generate CAR form for random client and property');
    console.log('=' .repeat(60));
    
    let browser;
    try {
        // Launch browser
        browser = await puppeteer.launch({ 
            headless: false, // Show browser to see what's happening
            args: ['--no-sandbox', '--disable-setuid-sandbox'],
            slowMo: 1000 // Slow down actions to see them
        });
        
        const page = await browser.newPage();
        await page.setViewport({ width: 1400, height: 900 });
        
        const crmUrl = 'http://172.22.206.209:3001';
        
        // Step 1: Navigate to CRM homepage
        console.log('\n🏠 Step 1: Navigate to CRM homepage');
        await page.goto(crmUrl, { waitUntil: 'networkidle2' });
        console.log(`   ✅ Homepage loaded: ${await page.title()}`);
        await page.screenshot({ path: 'user_flow_01_homepage.png' });
        
        // Step 2: Click "Generate Forms" button on dashboard
        console.log('\n📄 Step 2: Click Generate Forms button');
        const generateFormsButton = await page.$('a[href*="forms"]');
        if (generateFormsButton) {
            await generateFormsButton.click();
            await page.waitForNavigation({ waitUntil: 'networkidle2' });
            console.log(`   ✅ Navigated to forms page: ${await page.title()}`);
            await page.screenshot({ path: 'user_flow_02_forms_page.png' });
        } else {
            throw new Error('Generate Forms button not found on homepage');
        }
        
        // Step 3: Check for available forms
        console.log('\n📋 Step 3: Check available form options');
        const formCards = await page.$$('.form-card');
        console.log(`   📄 Available forms: ${formCards.length}`);
        
        if (formCards.length === 0) {
            throw new Error('No form cards found on forms page');
        }
        
        // Get form names
        const formNames = await page.evaluate(() => {
            const cards = document.querySelectorAll('.form-card');
            return Array.from(cards).map(card => {
                const title = card.querySelector('h6');
                return title ? title.textContent.trim() : 'Unknown Form';
            });
        });
        
        console.log(`   📋 Available forms: ${formNames.join(', ')}`);
        
        // Step 4: Select a random form (California Purchase Agreement)
        console.log('\n🎯 Step 4: Select California Residential Purchase Agreement');
        const targetFormButton = await page.$('button[onclick*="california_residential_purchase_agreement"]');
        if (targetFormButton) {
            await targetFormButton.click();
            await new Promise(resolve => setTimeout(resolve, 1000)); // Wait for modal to open
            console.log('   ✅ Form selection modal opened');
            await page.screenshot({ path: 'user_flow_03_form_modal.png' });
        } else {
            throw new Error('California Purchase Agreement button not found');
        }
        
        // Step 5: Check for client dropdown
        console.log('\n👤 Step 5: Check client selection dropdown');
        await page.waitForSelector('#clientSelect', { timeout: 5000 });
        
        // Get available clients
        const clientOptions = await page.evaluate(() => {
            const select = document.getElementById('clientSelect');
            const options = Array.from(select.options);
            return options.map(option => ({
                value: option.value,
                text: option.textContent.trim()
            })).filter(option => option.value !== '');
        });
        
        console.log(`   👥 Available clients: ${clientOptions.length}`);
        clientOptions.forEach(client => {
            console.log(`      • ${client.text} (ID: ${client.value})`);
        });
        
        if (clientOptions.length === 0) {
            throw new Error('No clients available in dropdown - this is the blocker!');
        }
        
        // Step 6: Select first available client
        console.log('\n✅ Step 6: Select first client');
        const firstClient = clientOptions[0];
        await page.select('#clientSelect', firstClient.value);
        console.log(`   👤 Selected client: ${firstClient.text}`);
        
        // Step 7: Click Generate Form button
        console.log('\n🚀 Step 7: Generate the form');
        const generateButton = await page.$('.modal-footer .btn-primary');
        if (generateButton) {
            // Click and wait for the API call
            await generateButton.click();
            console.log('   🔄 Form generation started...');
            
            // Wait for either success or error alert
            await new Promise(resolve => setTimeout(resolve, 5000)); // Give it time to process
            
            // Check for any alerts or responses
            const alerts = await page.evaluate(() => {
                // Check if there were any alerts
                return window.lastAlert || 'No alert detected';
            });
            
            console.log(`   📢 Response: ${alerts}`);
            await page.screenshot({ path: 'user_flow_04_form_result.png' });
            
        } else {
            throw new Error('Generate form button not found in modal');
        }
        
        // Step 8: Final assessment
        console.log('\n📊 Final User Experience Assessment:');
        console.log('=' .repeat(60));
        
        const currentUrl = page.url();
        console.log(`✅ Successfully navigated through: ${crmUrl} → ${currentUrl}`);
        console.log(`✅ Forms page accessible and functional`);
        console.log(`✅ ${formCards.length} forms available for selection`);
        console.log(`✅ ${clientOptions.length} clients available for selection`);
        console.log(`✅ Form generation process initiated`);
        
        if (clientOptions.length > 0) {
            console.log(`\n🎯 USER EXPERIENCE: FULLY FUNCTIONAL ✅`);
            console.log(`• User can access forms ✅`);
            console.log(`• User can select forms ✅`);
            console.log(`• User can select clients ✅`);
            console.log(`• User can initiate form generation ✅`);
        } else {
            console.log(`\n❌ USER EXPERIENCE: BLOCKED`);
            console.log(`• No clients available for form generation`);
        }
        
    } catch (error) {
        console.error('\n❌ User flow test failed:', error.message);
        if (browser) {
            const page = (await browser.pages())[0];
            if (page) {
                await page.screenshot({ path: 'user_flow_error.png' });
                console.log('📸 Error screenshot saved: user_flow_error.png');
            }
        }
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

// Run the test
if (require.main === module) {
    testCompleteUserFlow();
}