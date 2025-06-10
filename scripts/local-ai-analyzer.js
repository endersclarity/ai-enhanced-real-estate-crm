#!/usr/bin/env node

/**
 * Offer Creator Local AI Analyzer - V2 (Ported from FitForge)
 * A rational approach: Leverages Claude Code's superior analytical capabilities
 */

const fs = require('fs');
const path = require('path');

// Colors for beautiful console output
const colors = {
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m',
    reset: '\x1b[0m'
};

function log(message, color = 'reset') {
    console.log(`${colors[color]}🧠 Offer Creator AI Analyzer: ${message}${colors.reset}`);
}

function logError(message) {
    console.error(`${colors.red}❌ AI Analyzer Error: ${message}${colors.reset}`);
}

function logSuccess(message) {
    console.log(`${colors.green}✅ AI Analyzer: ${message}${colors.reset}`);
}

function constructPrompt(diagnosticLogContent, dockerLogContent, diagnosticLogPath, dockerLogPath) {
    const timestamp = new Date().toISOString();
    const prompt = `**Offer Creator Real Estate CRM Failure Analysis Request**

**Context:**
- A diagnostic test has failed while running against the Real Estate CRM application.
- Diagnostic Log File: ${diagnosticLogPath}
- Docker Log File: ${dockerLogPath}
- Generated: ${timestamp}

**I need you to perform a root cause analysis based on BOTH of the following logs.**

**1. Diagnostic Test Output:**
\`\`\`
${diagnosticLogContent}
\`\`\`

**2. Application Server (Docker) Log:**
\`\`\`
${dockerLogContent}
\`\`\`

**Analysis Requirements:**
Please analyze both logs to identify the root cause of the failure and provide a JSON response with the following EXACT structure:

{
  "summary": "Brief overview of the main failure and its root cause",
  "root_cause": "The fundamental underlying issue causing the application crash",
  "failure_type": "server_crash|client_error|network_failure|configuration_error|dependency_issue|database_error|flask_error",
  "priority": "critical|high|medium|low",
  "affected_components": ["list of specific components that are failing"],
  "evidence": {
    "diagnostic_indicators": ["specific lines or patterns from diagnostic log that indicate the problem"],
    "docker_log_indicators": ["specific lines or patterns from docker log that show the root cause"],
    "error_correlation": "How the diagnostic and docker logs relate to each other"
  },
  "immediate_fixes": [
    {
      "type": "code_fix|configuration_fix|dependency_fix|environment_fix|database_fix",
      "description": "What specifically needs to be fixed",
      "file_path": "Path to file that needs modification (MUST be in core_app/, scripts/, or templates/ directories)",
      "code_change": "Exact code or configuration change needed",
      "rationale": "Why this fix addresses the root cause"
    }
  ],
  "prevention_measures": [
    {
      "type": "diagnostic_improvement|validation_enhancement|error_handling|monitoring",
      "description": "How to prevent this issue in the future",
      "implementation": "Specific steps to implement this prevention measure"
    }
  ],
  "validation_steps": [
    "Step-by-step process to verify the fix works",
    "Include both automated and manual verification steps"
  ]
}

**Critical Safety Requirement:**
All 'file_path' values in your response MUST be within the 'core_app/', 'scripts/', or 'templates/' directories. Do not suggest changes to configuration files or other critical application source code.

**Focus Areas for Real Estate CRM:**
- Flask application crashes
- Database connection problems (SQLite)
- PDF form generation failures
- AI chatbot integration issues
- CRM data mapping problems
- Client/Property/Transaction API failures
- Template rendering issues
- Static asset loading problems
- Environment variable misconfigurations

Provide actionable, specific fixes that directly address the root cause identified in the logs.`;

    return prompt;
}

function main() {
    const [,, diagnosticLogPath, dockerLogPath] = process.argv;

    if (!diagnosticLogPath || !dockerLogPath) {
        logError('Missing required log file paths.');
        console.error(`${colors.yellow}Usage: node local-ai-analyzer.js <path-to-diagnostic-log> <path-to-docker-log>${colors.reset}`);
        console.error(`${colors.blue}Example: node local-ai-analyzer.js diagnostic-output.log docker-logs/app-crash.log${colors.reset}`);
        process.exit(1);
    }

    log('Starting local AI analysis for Real Estate CRM...', 'cyan');
    log(`Diagnostic Log: ${diagnosticLogPath}`, 'blue');
    log(`Docker Log: ${dockerLogPath}`, 'blue');

    try {
        // Verify both log files exist
        if (!fs.existsSync(diagnosticLogPath)) {
            throw new Error(`Diagnostic log file not found: ${diagnosticLogPath}`);
        }
        if (!fs.existsSync(dockerLogPath)) {
            throw new Error(`Docker log file not found: ${dockerLogPath}`);
        }

        // Read both log files
        log('Reading diagnostic log file...', 'yellow');
        const diagnosticLogContent = fs.readFileSync(diagnosticLogPath, 'utf8');
        log(`Diagnostic log: ${diagnosticLogContent.length} characters`, 'blue');

        log('Reading Docker log file...', 'yellow');
        const dockerLogContent = fs.readFileSync(dockerLogPath, 'utf8');
        log(`Docker log: ${dockerLogContent.length} characters`, 'blue');

        // Generate the comprehensive analysis prompt
        log('Constructing analysis prompt for Claude Code...', 'magenta');
        const prompt = constructPrompt(diagnosticLogContent, dockerLogContent, diagnosticLogPath, dockerLogPath);

        logSuccess('Analysis prompt generated successfully!');
        log('='.repeat(80), 'cyan');
        console.log(prompt);
        log('='.repeat(80), 'cyan');
        logSuccess('Copy the above prompt and provide it to Claude Code for analysis.');

    } catch (error) {
        logError(`Failed to generate prompt: ${error.message}`);
        process.exit(1);
    }
}

// Handle uncaught errors gracefully
process.on('uncaughtException', (error) => {
    logError(`Uncaught exception: ${error.message}`);
    process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
    logError(`Unhandled rejection at ${promise}: ${reason}`);
    process.exit(1);
});

main();
