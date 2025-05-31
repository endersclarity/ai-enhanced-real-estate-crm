// Entity Extraction Test Suite
// Validates Tasks 5-8: Extraction, Validation, Preview, CRM Mapping

const testEmails = [
    {
        id: "inquiry_email",
        type: "inquiryEmail",
        content: `From: john.doe@gmail.com
Subject: Property Inquiry - 123 Main Street

Hi Narissa,

I'm interested in the property at 123 Main Street, Los Angeles, CA 90210. 
My budget is up to $750,000 and I'm pre-approved for financing.
You can reach me at (555) 123-4567 or john.doe@gmail.com.

Looking to close by December 15th, 2024.

Thanks,
John Doe`,
        expectedEntities: {
            email: ["john.doe@gmail.com"],
            phone: ["(555) 123-4567"],
            address: ["123 Main Street, Los Angeles, CA 90210"],
            price: ["$750,000"],
            date: ["December 15th, 2024"],
            name: ["John Doe"]
        }
    },
    {
        id: "listing_email", 
        type: "listingEmail",
        content: `New Listing Alert - MLS# 12345678

Property: 456 Oak Avenue, Beverly Hills, CA 90210
List Price: $1,250,000
Bedrooms: 4
Bathrooms: 3
Square Feet: 2,800

Contact: agent@realty.com
Phone: 310-555-0199`,
        expectedEntities: {
            mlsNumber: ["12345678"],
            address: ["456 Oak Avenue, Beverly Hills, CA 90210"],
            price: ["$1,250,000"],
            email: ["agent@realty.com"],
            phone: ["310-555-0199"]
        }
    },
    {
        id: "malformed_email",
        type: "generalEmail", 
        content: `Bad email with invalid data:
Email: not-an-email
Phone: 123
Price: expensive
Address: somewhere`,
        expectedEntities: {
            // Should detect validation issues
        }
    }
];

function runEntityExtractionTests() {
    console.log("🧪 Starting Entity Extraction Test Suite");
    console.log("==========================================");
    
    const results = {
        task5: { passed: 0, failed: 0, details: [] },
        task6: { passed: 0, failed: 0, details: [] },
        task7: { passed: 0, failed: 0, details: [] },
        task8: { passed: 0, failed: 0, details: [] }
    };
    
    testEmails.forEach(testEmail => {
        console.log(`\n📧 Testing: ${testEmail.id}`);
        console.log("Content:", testEmail.content.substring(0, 100) + "...");
        
        try {
            // Task 5: Entity Extraction
            if (typeof RealEstateAIContext !== 'undefined' && RealEstateAIContext.extractEntities) {
                const extraction = RealEstateAIContext.extractEntities(testEmail.content);
                
                // Validate extraction results
                const extractionScore = validateExtraction(extraction, testEmail.expectedEntities);
                if (extractionScore >= 0.8) { // 80% threshold
                    results.task5.passed++;
                    results.task5.details.push(`✅ ${testEmail.id}: ${Math.round(extractionScore * 100)}% accuracy`);
                } else {
                    results.task5.failed++;
                    results.task5.details.push(`❌ ${testEmail.id}: ${Math.round(extractionScore * 100)}% accuracy (below 80%)`);
                }
                
                // Task 6: Data Validation
                const validation = validateExtractedData(extraction.entities);
                if (validation) {
                    results.task6.passed++;
                    results.task6.details.push(`✅ ${testEmail.id}: Validation logic working`);
                } else {
                    results.task6.failed++;
                    results.task6.details.push(`❌ ${testEmail.id}: Validation failed`);
                }
                
                // Task 7: Preview Interface (check structure)
                if (extraction.entities && typeof extraction.entities === 'object') {
                    results.task7.passed++;
                    results.task7.details.push(`✅ ${testEmail.id}: Preview data structure valid`);
                } else {
                    results.task7.failed++;
                    results.task7.details.push(`❌ ${testEmail.id}: Preview data structure invalid`);
                }
                
                // Task 8: CRM Mapping
                if (typeof RealEstateAIContext.mapToCRM === 'function') {
                    const mapping = RealEstateAIContext.mapToCRM(extraction.entities, extraction.emailType);
                    if (mapping && Object.keys(mapping).length > 0) {
                        results.task8.passed++;
                        results.task8.details.push(`✅ ${testEmail.id}: CRM mapping generated (${Object.keys(mapping).length} fields)`);
                    } else {
                        results.task8.failed++;
                        results.task8.details.push(`❌ ${testEmail.id}: CRM mapping failed`);
                    }
                } else {
                    results.task8.failed++;
                    results.task8.details.push(`❌ ${testEmail.id}: mapToCRM function not found`);
                }
                
            } else {
                results.task5.failed++;
                results.task5.details.push(`❌ ${testEmail.id}: RealEstateAIContext not available`);
            }
            
        } catch (error) {
            console.error(`Error testing ${testEmail.id}:`, error);
            results.task5.failed++;
            results.task6.failed++;
            results.task7.failed++;
            results.task8.failed++;
        }
    });
    
    // Generate test report
    console.log("\n📊 TEST RESULTS SUMMARY");
    console.log("========================");
    
    Object.entries(results).forEach(([task, result]) => {
        const total = result.passed + result.failed;
        const percentage = total > 0 ? Math.round((result.passed / total) * 100) : 0;
        const status = percentage >= 80 ? "✅ PASS" : "❌ FAIL";
        
        console.log(`${task.toUpperCase()}: ${status} (${result.passed}/${total} tests passed - ${percentage}%)`);
        result.details.forEach(detail => console.log(`  ${detail}`));
    });
    
    return results;
}

function validateExtraction(extraction, expected) {
    if (!extraction || !extraction.entities) return 0;
    
    let totalExpected = 0;
    let totalFound = 0;
    
    Object.entries(expected).forEach(([type, expectedValues]) => {
        totalExpected += expectedValues.length;
        if (extraction.entities[type]) {
            // Count how many expected values were found
            expectedValues.forEach(expectedValue => {
                const found = extraction.entities[type].some(foundValue => 
                    foundValue.toLowerCase().includes(expectedValue.toLowerCase()) ||
                    expectedValue.toLowerCase().includes(foundValue.toLowerCase())
                );
                if (found) totalFound++;
            });
        }
    });
    
    return totalExpected > 0 ? totalFound / totalExpected : 0;
}

// For browser testing
if (typeof window !== 'undefined') {
    window.runEntityExtractionTests = runEntityExtractionTests;
}

// For Node.js testing
if (typeof module !== 'undefined') {
    module.exports = { runEntityExtractionTests };
}