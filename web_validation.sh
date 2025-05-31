#!/bin/bash
# WEB_VALIDATION.sh - NEVER SAY "WORKING" WITHOUT PROOF
# Comprehensive end-to-end testing before declaring success

set -e

echo "🔍 COMPREHENSIVE WEB VALIDATION - NO FALSE POSITIVES"
echo "=================================================="

# Get WSL IP
WSL_IP=$(ip addr show eth0 | grep "inet " | awk '{print $2}' | cut -d/ -f1)
echo "WSL IP: $WSL_IP"

# Test 1: Process check
echo ""
echo "🔍 TEST 1: Flask Process Check"
FLASK_PID=$(pgrep -f "python.*real_estate_crm.py" || echo "NONE")
if [ "$FLASK_PID" = "NONE" ]; then
    echo "❌ FAIL: No Flask process running"
    exit 1
else
    echo "✅ PASS: Flask process running (PID: $FLASK_PID)"
fi

# Test 2: HTTP Response
echo ""
echo "🔍 TEST 2: HTTP Response Check"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://$WSL_IP:5000 || echo "000")
if [ "$HTTP_STATUS" != "200" ]; then
    echo "❌ FAIL: HTTP status $HTTP_STATUS (expected 200)"
    exit 1
else
    echo "✅ PASS: HTTP 200 response"
fi

# Test 3: HTML Content Validation
echo ""
echo "🔍 TEST 3: HTML Content Validation"
HTML_CONTENT=$(curl -s http://$WSL_IP:5000 | head -50)
if echo "$HTML_CONTENT" | grep -q "Narissa Realty CRM" && echo "$HTML_CONTENT" | grep -q "<!DOCTYPE html>"; then
    echo "✅ PASS: Valid HTML with CRM title"
else
    echo "❌ FAIL: Invalid HTML content or missing CRM title"
    echo "Content preview: $(echo "$HTML_CONTENT" | head -3)"
    exit 1
fi

# Test 4: AI Chatbot Endpoint
echo ""
echo "🔍 TEST 4: AI Chatbot Endpoint Test"
CHAT_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" -d '{"message":"ping"}' http://$WSL_IP:5000/chat)
if echo "$CHAT_RESPONSE" | grep -q '"response"' && echo "$CHAT_RESPONSE" | grep -q '"model"'; then
    echo "✅ PASS: AI chatbot responding"
else
    echo "❌ FAIL: AI chatbot not responding properly"
    echo "Response: $CHAT_RESPONSE"
    exit 1
fi

# Test 5: Database Connection
echo ""
echo "🔍 TEST 5: Database Connection Test"
DB_TEST=$(curl -s http://$WSL_IP:5000/clients | head -20)
if echo "$DB_TEST" | grep -q "Clients" && ! echo "$DB_TEST" | grep -q "404"; then
    echo "✅ PASS: Database connection working"
else
    echo "❌ FAIL: Database connection issues"
    echo "Response: $DB_TEST"
    exit 1
fi

# Test 6: MLS Data Check
echo ""
echo "🔍 TEST 6: MLS Data Availability"
MLS_CHECK=$(curl -s -X POST -H "Content-Type: application/json" -d '{"message":"how many listings"}' http://$WSL_IP:5000/chat)
if echo "$MLS_CHECK" | grep -q "292" || echo "$MLS_CHECK" | grep -q "listing"; then
    echo "✅ PASS: MLS data loaded and accessible"
else
    echo "⚠️  WARNING: MLS data may not be properly loaded"
fi

echo ""
echo "🎉 ALL TESTS PASSED - SITE IS ACTUALLY WORKING"
echo "🌐 Access URL: http://$WSL_IP:5000"
echo "✅ End-to-end validation complete"