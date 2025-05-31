/**
 * AI Instruction Framework for Real Estate CRM Chatbot
 * Phase 2: AI Integration - Smart Context Loading System
 * 
 * This framework embeds comprehensive real estate domain knowledge
 * and 177-field CRM schema awareness into the browser interface
 */

const RealEstateAIContext = {
    // Core System Configuration
    version: "1.0.0",
    lastUpdated: "2025-05-31",
    schemaVersion: "177-field-crm",
    
    // Real Estate Domain Knowledge
    domainKnowledge: {
        propertyTypes: [
            "Single Family Residential", "Townhouse", "Condominium", 
            "Multi-Family", "Commercial", "Industrial", "Land", 
            "Mobile Home", "Cooperative", "Manufactured Home"
        ],
        
        transactionTypes: [
            "Purchase", "Sale", "Lease", "Rental", "Refinance", 
            "Short Sale", "Foreclosure", "Investment", "1031 Exchange"
        ],
        
        californiaRegions: [
            "Bay Area", "Los Angeles", "San Diego", "Central Valley", 
            "Sacramento", "Orange County", "Inland Empire", "Central Coast"
        ],
        
        commonTerms: {
            "MLS": "Multiple Listing Service",
            "HOA": "Homeowners Association", 
            "PMI": "Private Mortgage Insurance",
            "DTI": "Debt-to-Income Ratio",
            "LTV": "Loan-to-Value Ratio",
            "CMA": "Comparative Market Analysis",
            "DOM": "Days on Market",
            "PITI": "Principal, Interest, Taxes, Insurance"
        }
    },

    // 177-Field CRM Schema Awareness
    crmSchema: {
        clientFields: {
            personal: ["firstName", "lastName", "email", "phone", "dateOfBirth", "ssn"],
            address: ["streetAddress", "city", "state", "zipCode", "county"],
            financial: ["income", "creditScore", "downPayment", "preApprovalAmount"],
            preferences: ["propertyType", "priceRange", "location", "bedrooms", "bathrooms"]
        },
        
        propertyFields: {
            basic: ["mlsNumber", "address", "city", "state", "zipCode", "propertyType"],
            details: ["bedrooms", "bathrooms", "squareFootage", "lotSize", "yearBuilt"],
            pricing: ["listPrice", "salePrice", "pricePerSqFt", "hoaFees", "taxes"],
            features: ["garage", "pool", "fireplace", "basement", "stories"]
        },
        
        transactionFields: {
            core: ["transactionId", "type", "status", "listingDate", "contractDate"],
            parties: ["listingAgent", "buyerAgent", "lender", "escrowOfficer", "inspector"],
            financial: ["salePrice", "downPayment", "loanAmount", "closingCosts"],
            timeline: ["listingDate", "contractDate", "inspectionDate", "closingDate"]
        }
    },

    // Email Processing Instructions
    emailProcessing: {
        entityExtraction: {
            patterns: {
                price: /\$[\d,]+(?:\.\d{2})?/g,
                phone: /\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}/g,
                email: /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g,
                address: /\d+\s+[A-Za-z0-9\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Circle|Cir|Court|Ct|Place|Pl)/gi,
                mlsNumber: /MLS[#:\s]*([A-Z0-9]+)/gi,
                date: /\d{1,2}\/\d{1,2}\/\d{2,4}|\d{4}-\d{2}-\d{2}/g
            },
            
            confidence: {
                high: ["MLS numbers", "formatted addresses", "phone numbers"],
                medium: ["property types", "transaction amounts", "dates"],
                low: ["general descriptions", "preferences", "notes"]
            }
        },
        
        contentClassification: {
            inquiryEmail: {
                indicators: ["interested in", "looking for", "want to see", "schedule showing"],
                actions: ["createClient", "addProperty", "scheduleTask"]
            },
            
            listingEmail: {
                indicators: ["new listing", "price change", "status update", "MLS"],
                actions: ["addProperty", "updateProperty", "notifyClients"]
            },
            
            transactionEmail: {
                indicators: ["offer", "contract", "closing", "inspection", "appraisal"],
                actions: ["updateTransaction", "addTask", "notifyParties"]
            }
        }
    },

    // Workflow Automation Instructions
    workflowAutomation: {
        taskGeneration: {
            newClient: [
                "Send welcome package",
                "Schedule consultation meeting", 
                "Setup MLS search alerts",
                "Gather pre-approval documents"
            ],
            
            newListing: [
                "Create listing presentation",
                "Schedule photography",
                "Input into MLS",
                "Notify potential buyers"
            ],
            
            activeTransaction: [
                "Monitor contract dates",
                "Coordinate inspections",
                "Track loan progress",
                "Prepare closing documents"
            ]
        },
        
        followUpScheduling: {
            immediately: ["Hot leads", "Contract deadlines", "Inspection issues"],
            today: ["New inquiries", "Property updates", "Client responses"],
            thisWeek: ["Follow-up calls", "Market updates", "Property showings"],
            monthly: ["Market reports", "Client check-ins", "Referral requests"]
        }
    },

    // Performance Targets
    performanceTargets: {
        emailProcessing: {
            extractionTime: "< 10 seconds",
            accuracy: "> 95%",
            endToEndWorkflow: "< 30 seconds"
        },
        
        chatbotResponse: {
            responseTime: "< 5 seconds",
            contextAwareness: "177-field schema",
            domainAccuracy: "> 90%"
        }
    },

    // Integration Instructions for CRM Demo
    crmIntegration: {
        localStorage: {
            clientsKey: "crmClients",
            propertiesKey: "crmProperties", 
            transactionsKey: "crmTransactions",
            structure: "177-field schema compliance"
        },
        
        quickActions: [
            "Add Client from Email",
            "Create Property Listing", 
            "Start New Transaction",
            "Schedule Follow-up",
            "Generate Forms"
        ],
        
        uiIntegration: {
            theme: "Bootstrap with Narissa Realty branding",
            primaryColor: "#2c5aa0",
            layout: "Responsive cards with sidebar navigation",
            icons: "Bootstrap Icons (bi-*)"
        }
    },

    // Context Loading Methods
    loadContext: function() {
        console.log("🧠 Loading Real Estate AI Context...");
        
        // Load domain knowledge
        this.activeDomainKnowledge = this.domainKnowledge;
        
        // Load CRM schema awareness
        this.activeSchema = this.crmSchema;
        
        // Initialize email processing
        this.emailProcessor = this.emailProcessing;
        
        // Setup workflow automation
        this.workflowEngine = this.workflowAutomation;
        
        console.log("✅ AI Context Loaded - Ready for real estate CRM operations");
        
        return {
            status: "loaded",
            version: this.version,
            schemaFields: Object.keys(this.crmSchema).length,
            domainTerms: Object.keys(this.domainKnowledge.commonTerms).length,
            ready: true
        };
    },
    
    // Entity Extraction Method
    extractEntities: function(emailContent) {
        const entities = {};
        
        // Extract structured data using patterns
        Object.entries(this.emailProcessing.entityExtraction.patterns).forEach(([type, pattern]) => {
            const matches = emailContent.match(pattern);
            if (matches) {
                entities[type] = matches;
            }
        });
        
        // Classify email type
        let emailType = "general";
        Object.entries(this.emailProcessing.contentClassification).forEach(([type, config]) => {
            if (config.indicators.some(indicator => 
                emailContent.toLowerCase().includes(indicator.toLowerCase())
            )) {
                emailType = type;
            }
        });
        
        return {
            entities: entities,
            emailType: emailType,
            confidence: this.calculateConfidence(entities),
            suggestedActions: this.emailProcessing.contentClassification[emailType]?.actions || []
        };
    },
    
    // Confidence Calculation
    calculateConfidence: function(entities) {
        let score = 0;
        let total = 0;
        
        Object.entries(entities).forEach(([type, values]) => {
            total += values.length;
            
            if (this.emailProcessing.entityExtraction.confidence.high.includes(type)) {
                score += values.length * 0.9;
            } else if (this.emailProcessing.entityExtraction.confidence.medium.includes(type)) {
                score += values.length * 0.7;
            } else {
                score += values.length * 0.5;
            }
        });
        
        return total > 0 ? Math.round((score / total) * 100) : 0;
    },
    
    // CRM Field Mapping
    mapToCRM: function(entities, emailType) {
        const mapping = {};
        
        // Map entities to appropriate CRM fields based on type and schema
        if (entities.email) {
            mapping.email = entities.email[0];
        }
        
        if (entities.phone) {
            mapping.phone = entities.phone[0];
        }
        
        if (entities.address) {
            mapping.propertyAddress = entities.address[0];
        }
        
        if (entities.price) {
            mapping.price = entities.price[0].replace(/[$,]/g, '');
        }
        
        if (entities.mlsNumber) {
            mapping.mlsNumber = entities.mlsNumber[0];
        }
        
        // Add email type context
        mapping.sourceType = emailType;
        mapping.processingDate = new Date().toISOString();
        
        return mapping;
    }
};

// Export for use in chatbot interface
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RealEstateAIContext;
}

// Global availability for browser
window.RealEstateAIContext = RealEstateAIContext;