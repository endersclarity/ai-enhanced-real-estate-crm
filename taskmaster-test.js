#!/usr/bin/env node

console.log('=== Taskmaster AI Integration Test ===');

// Test 1: Check environment variables
const geminiKey = process.env.GEMINI_API_KEY;
console.log('✓ GEMINI_API_KEY configured:', geminiKey ? 'YES (length: ' + geminiKey.length + ')' : 'NO');

// Test 2: Check Taskmaster config
const fs = require('fs');
const path = require('path');

try {
    const configPath = path.join(process.cwd(), '.taskmaster', 'config.json');
    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    console.log('✓ Taskmaster config found');
    console.log('  - Main model:', config.models.main.provider, config.models.main.modelId);
    console.log('  - Research model:', config.models.research.provider, config.models.research.modelId);
    console.log('  - Fallback model:', config.models.fallback.provider, config.models.fallback.modelId);
} catch (error) {
    console.log('✗ Taskmaster config error:', error.message);
}

// Test 3: Check tasks.json 
try {
    const tasksPath = path.join(process.cwd(), '.taskmaster', 'tasks', 'tasks.json');
    const tasks = JSON.parse(fs.readFileSync(tasksPath, 'utf8'));
    console.log('✓ Tasks file found with', tasks.tasks.length, 'tasks');
    
    const pending = tasks.tasks.filter(t => t.status === 'pending').length;
    const done = tasks.tasks.filter(t => t.status === 'done').length;
    
    console.log('  - Done:', done, 'Pending:', pending);
} catch (error) {
    console.log('✗ Tasks file error:', error.message);
}

console.log('\\n=== Integration Test Complete ===');
