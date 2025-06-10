# System: AI-Enhanced Real Estate CRM & Form Automation

## Purpose
Provides comprehensive real estate customer relationship management with AI-powered form automation, enabling rapid generation of California Association of Realtors forms with intelligent data pre-population and three-tier diagnostic capabilities.

## Architecture
```
[Frontend] <-> [Flask App] <-> [AI Engine] <-> [Database]
    |             |              |             |
    |             |              |             +-- [SQLite Schema (177 fields)]
    |             |              +-- [Gemini 2.5 Flash + LangChain]
    |             |              +-- [Three-Tier Diagnostics]
    |             +-- [Form Processing Module]
    |             +-- [CRM Core Module] 
    |             +-- [AI Integration Module]
    +-- [Bootstrap UI]
    +-- [Real-time Dashboard]
```

## Module Registry
- [crm_core (`memory-bank/crm_core_module.md`)]: Core CRM functionality with 177-field schema
- [form_processing (`memory-bank/form_processing_module.md`)]: Multi-strategy PDF/HTML form generation
- [ai_integration (`memory-bank/ai_integration_module.md`)]: Gemini AI with LangChain function calling
- [three_tier_diagnostics (`memory-bank/three_tier_diagnostics_module.md`)]: FitForge-transplanted debugging system
- [deployment (`memory-bank/deployment_module.md`)]: Production deployment and configuration

## Development Workflow
1. Run three-tier diagnostics for system health verification
2. Execute AI-assisted code analysis for complex issues
3. Implement features using existing form infrastructure
4. Test with comprehensive CRM data validation
5. Deploy with production-ready security configuration

## Version: 2.0 | Status: Critical Remediation Phase

## Critical Context
**Current Status**: System requires immediate remediation due to database schema mismatches, JavaScript dependency conflicts, and enhanced architecture integration failures. Contains $50,000+ worth of existing form processing infrastructure that needs proper integration activation.
