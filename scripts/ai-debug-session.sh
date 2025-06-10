#!/bin/bash
# AI-assisted debugging session launcher

echo "🤖 AI Debug Session Manager"
echo "=========================="

# Create session directory
SESSION_ID=$(date +%Y%m%d_%H%M%S)
SESSION_DIR="ai-debug/sessions/$SESSION_ID"
mkdir -p "$SESSION_DIR"

# Function to capture error context
capture_error_context() {
    echo "📸 Capturing error context..."
    
    # Get Docker logs
    docker-compose -f docker-compose.dev.yml logs --tail=50 app > "$SESSION_DIR/docker_logs.txt"
    
    # Get system status
    docker-compose -f docker-compose.dev.yml ps > "$SESSION_DIR/docker_status.txt"
    
    # Create error context JSON
    cat > "$SESSION_DIR/error_context.json" << EOF
{
    "session_id": "$SESSION_ID",
    "timestamp": "$(date -Iseconds)",
    "environment": "docker-dev",
    "error_description": "$1",
    "docker_logs": "$(tail -20 $SESSION_DIR/docker_logs.txt | jq -Rs .)",
    "system_status": "$(cat $SESSION_DIR/docker_status.txt | jq -Rs .)"
}
EOF
    
    echo "✅ Error context saved to: $SESSION_DIR/error_context.json"
}

# Main menu
echo "What would you like to debug?"
echo "1. Application startup issues"
echo "2. Database connection problems"
echo "3. API endpoint failures"
echo "4. Custom error (describe)"
echo "5. View previous sessions"

read -p "Select option (1-5): " choice

case $choice in
    1)
        capture_error_context "Application startup failure"
        ;;
    2)
        capture_error_context "Database connection error"
        ;;
    3)
        capture_error_context "API endpoint failure"
        ;;
    4)
        read -p "Describe the error: " custom_error
        capture_error_context "$custom_error"
        ;;
    5)
        echo -e "\n📁 Previous debug sessions:"
        ls -la ai-debug/sessions/
        exit 0
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac

# Show next steps
echo -e "\n🔧 Next Steps:"
echo "1. Review error context: cat $SESSION_DIR/error_context.json"
echo "2. Use AI to analyze: python scripts/analyze_error.py $SESSION_DIR/error_context.json"
echo "3. Apply fixes manually after review"