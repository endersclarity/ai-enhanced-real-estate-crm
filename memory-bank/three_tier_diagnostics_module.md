# Module: Three-Tier Diagnostics

## Purpose & Responsibility
Provides automated system health monitoring and AI-assisted debugging capabilities transplanted from the FitForge project. Implements fast-fail diagnostics, automated log capture, and AI-powered root cause analysis to quickly identify and resolve system issues across the real estate CRM infrastructure.

## Interfaces
* `FastFailDiagnostics`: Rapid system health verification
  * `run_tier_1_checks()`: Quick Docker, database, and service connectivity tests
  * `detect_critical_failures()`: Identify system-breaking issues within seconds
* `AIDebugAnalyzer`: Automated troubleshooting intelligence
  * `capture_system_state()`: Gather logs, errors, and configuration data
  * `generate_claude_prompt()`: Create structured AI analysis prompts
  * `suggest_remediation()`: Provide step-by-step fix recommendations
* `HumanHandoff`: Clear escalation path for complex issues
  * `create_debug_session()`: Generate comprehensive issue documentation
  * `provide_next_steps()`: Clear action items for human intervention
* Input: System health queries, error conditions, diagnostic triggers
* Output: Health status reports, AI analysis prompts, remediation suggestions

## Implementation Details
* Files:
  * `scripts/three-tier-diagnostics.sh` - Main orchestration script
  * `scripts/fast-diagnostics.py` - Tier 1 rapid health checks
  * `scripts/local-ai-analyzer.js` - Tier 2 AI analysis engine (ported from FitForge)
  * `ai-debug/capture_error.py` - System state capture utilities
  * `ai-debug/generate-debug-prompt.py` - AI prompt generation
  * `ai-debug/suggested_fix.py` - Remediation recommendation engine
  * `ai-debug/sessions/` - Debug session history and logs
* Important algorithms:
  * Fast-fail testing with aggressive timeouts for rapid issue detection
  * Automated log aggregation from Docker, Flask, and database sources
  * AI prompt engineering for effective Claude Code root cause analysis
  * Session-based debugging with persistent context across investigations
* Data Models:
  * `DiagnosticSession` - Complete debugging context and history
  * `SystemHealth` - Multi-tier health status tracking
  * `AIAnalysis` - Structured AI recommendations and confidence scoring

## Current Implementation Status
* Completed: **SUCCESSFULLY TRANSPLANTED** - Three-tier system operational and immediately detected real database issues
* In Progress: Integration with enhanced CRM monitoring for proactive issue detection
* Pending: Automated remediation for common issues, integration with deployment monitoring

## Implementation Plans & Tasks
* `implementation_plan_diagnostic_integration.md`
  * [CRM Monitoring]: Integrate diagnostics with CRM health checks
  * [Proactive Alerts]: Set up automated health monitoring schedules
  * [Auto-Remediation]: Implement fixes for common database/dependency issues
* `implementation_plan_diagnostic_enhancement.md`
  * [AI Improvements]: Enhance AI analysis quality based on real estate specific issues
  * [Dashboard Integration]: Add health status indicators to CRM dashboard
  * [Performance Monitoring]: Expand beyond error detection to performance optimization

## Mini Dependency Tracker
---mini_tracker_start---
Dependencies:
- crm_core_module.md (monitors CRM database and Flask application health)
- deployment_module.md (integrates with production monitoring)

Dependents:
- Critical for maintaining system reliability
- Enables rapid issue resolution and user confidence
- Supports production deployment with automated monitoring
- Validates system integrity during development cycles
---mini_tracker_end---
