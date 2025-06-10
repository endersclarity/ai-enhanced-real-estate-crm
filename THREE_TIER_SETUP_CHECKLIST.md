# 🚀 Three-Tier AI-Assisted Debugging Setup Checklist

## Overview
This checklist implements the proven Docker-only environment with fail-fast diagnostics and human-in-the-loop AI workflow for the Real Estate CRM project.

## 📋 Phase 1: Docker-Based Universal Environment

### 1.1 Create Dockerfile
```dockerfile
# Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose ports
EXPOSE 5000

# Default command
CMD ["python", "core_app/real_estate_crm.py"]
```

### 1.2 Create docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=1
      - DATABASE_URL=postgresql://postgres:password@db:5432/real_estate
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - USE_SUPABASE=false
    volumes:
      - .:/app
    depends_on:
      - db
    command: python core_app/real_estate_crm.py

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=real_estate
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  test:
    build: .
    environment:
      - TEST_MODE=1
      - DATABASE_URL=postgresql://postgres:password@db:5432/real_estate_test
    volumes:
      - .:/app
    depends_on:
      - db
    command: python -m pytest

volumes:
  postgres_data:
```

### 1.3 Environment Setup Commands
```bash
# Create .env file
cat > .env << EOF
GEMINI_API_KEY=AIzaSyCJ8-hQJVLGXDkHy2sjw-O6Dls0FVO0gGU
FLASK_ENV=development
USE_SUPABASE=false
EOF

# Build and start services
docker-compose build
docker-compose up -d

# View logs
docker-compose logs -f web

# Run database migrations
docker-compose exec web python core_app/init_database.py
```

## 📋 Phase 2: Fail-Fast Diagnostic Suite

### 2.1 Create test_diagnostics.py
```python
#!/usr/bin/env python3
"""
Fail-fast diagnostic tests for Real Estate CRM
"""
import sys
import requests
import json
from time import sleep

class DiagnosticSuite:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.failures = []
        
    def run_all_tests(self):
        """Run all diagnostic tests"""
        print("🔍 Starting Diagnostic Suite...\n")
        
        # Test 1: Server connectivity
        if not self.test_server_up():
            self.fail_fast("Server not responding")
            
        # Test 2: Database connectivity
        if not self.test_database():
            self.fail_fast("Database connection failed")
            
        # Test 3: AI integration
        if not self.test_ai_integration():
            self.fail_fast("AI integration not working")
            
        # Test 4: CRPA endpoints
        if not self.test_crpa_endpoints():
            self.fail_fast("CRPA system not functional")
            
        print("\n✅ All diagnostics passed!")
        return True
        
    def test_server_up(self):
        """Test if server is responding"""
        print("1. Testing server connectivity...")
        try:
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                print("   ✓ Server is up")
                return True
        except:
            pass
        print("   ✗ Server not responding")
        return False
        
    def test_database(self):
        """Test database connectivity"""
        print("2. Testing database...")
        try:
            response = requests.get(f"{self.base_url}/api/crpa/transactions")
            data = response.json()
            if 'success' in data:
                print(f"   ✓ Database connected ({data.get('count', 0)} transactions)")
                return True
        except:
            pass
        print("   ✗ Database connection failed")
        return False
        
    def test_ai_integration(self):
        """Test AI chatbot"""
        print("3. Testing AI integration...")
        try:
            response = requests.post(
                f"{self.base_url}/chat",
                json={"message": "Hello"},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                print("   ✓ AI chatbot responding")
                return True
        except:
            pass
        print("   ✗ AI integration failed")
        return False
        
    def test_crpa_endpoints(self):
        """Test CRPA form generation"""
        print("4. Testing CRPA endpoints...")
        try:
            # Test dashboard loads
            response = requests.get(f"{self.base_url}/crpa_dashboard")
            if response.status_code == 200:
                print("   ✓ CRPA dashboard accessible")
                return True
        except:
            pass
        print("   ✗ CRPA system not functional")
        return False
        
    def fail_fast(self, message):
        """Stop execution on critical failure"""
        print(f"\n❌ CRITICAL FAILURE: {message}")
        print("Diagnostic suite halted. Fix this issue before proceeding.")
        sys.exit(1)

if __name__ == "__main__":
    # Wait for services to start
    print("Waiting for services to start...")
    sleep(5)
    
    # Run diagnostics
    suite = DiagnosticSuite()
    suite.run_all_tests()
```

### 2.2 Create Playwright UI Tests
```python
# test_ui_diagnostics.py
import asyncio
from playwright.async_api import async_playwright

async def test_crpa_ui():
    """Test CRPA dashboard UI functionality"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Navigate to CRPA dashboard
        await page.goto("http://localhost:5000/crpa_dashboard")
        
        # Test 1: Check jQuery loaded
        jquery_loaded = await page.evaluate("typeof $ !== 'undefined'")
        assert jquery_loaded, "jQuery not loaded"
        
        # Test 2: Check Bootstrap loaded
        bootstrap_loaded = await page.evaluate("typeof bootstrap !== 'undefined'")
        assert bootstrap_loaded, "Bootstrap not loaded"
        
        # Test 3: Test architecture button
        await page.click("text=Test Enhanced Architecture")
        await page.wait_for_selector(".modal.show", timeout=5000)
        
        # Test 4: Check for errors
        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg) if msg.type == "error" else None)
        
        await browser.close()
        
        if console_errors:
            print(f"❌ Console errors detected: {console_errors}")
            return False
            
        print("✅ UI tests passed")
        return True

# Run the test
asyncio.run(test_crpa_ui())
```

### 2.3 Integration Test Script
```bash
#!/bin/bash
# run_diagnostics.sh

echo "🚀 Running Three-Tier Diagnostic Suite"
echo "====================================="

# Step 1: Check Docker services
echo "1. Checking Docker services..."
docker-compose ps

# Step 2: Run Python diagnostics
echo -e "\n2. Running Python diagnostics..."
docker-compose exec web python test_diagnostics.py

# Step 3: Run Playwright UI tests
echo -e "\n3. Running UI tests..."
docker-compose exec web python test_ui_diagnostics.py

# Step 4: Generate report
echo -e "\n📊 Diagnostic Report Complete"
```

## 📋 Phase 3: Human-in-the-Loop AI Workflow

### 3.1 Create AI Debug Assistant
```python
# ai_debug_assistant.py
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

class AIDebugAssistant:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="models/gemini-2.5-flash-preview-04-17",
            google_api_key="AIzaSyCJ8-hQJVLGXDkHy2sjw-O6Dls0FVO0gGU",
            temperature=0.1
        )
        
    def analyze_error(self, error_context):
        """Analyze error and suggest fixes"""
        messages = [
            SystemMessage(content="""You are a debugging assistant for a Real Estate CRM system.
            Analyze the error and provide:
            1. Root cause analysis
            2. Suggested fix with code
            3. Prevention strategy"""),
            HumanMessage(content=f"Error context: {json.dumps(error_context, indent=2)}")
        ]
        
        response = self.llm.invoke(messages)
        return response.content
        
    def validate_fix(self, original_code, proposed_fix):
        """Validate proposed fix before applying"""
        messages = [
            SystemMessage(content="Review this code fix and identify any potential issues"),
            HumanMessage(content=f"""
            Original: {original_code}
            Proposed Fix: {proposed_fix}
            
            Is this fix safe to apply? What could go wrong?
            """)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
```

### 3.2 Create Human Control Interface
```python
# human_control.py
import click
from ai_debug_assistant import AIDebugAssistant

@click.command()
@click.option('--error-file', help='File containing error details')
def debug_with_ai(error_file):
    """Interactive AI-assisted debugging"""
    assistant = AIDebugAssistant()
    
    # Load error context
    with open(error_file, 'r') as f:
        error_context = json.load(f)
    
    # Get AI analysis
    click.echo("🤖 AI Analysis:")
    analysis = assistant.analyze_error(error_context)
    click.echo(analysis)
    
    # Human decision point
    if click.confirm("\n👤 Do you want to see suggested code fix?"):
        # Show fix
        click.echo("\n📝 Suggested Fix:")
        click.echo(analysis)
        
        # Human approval required
        if click.confirm("\n⚠️ Apply this fix?"):
            click.echo("✅ Fix approved by human")
            # Apply fix logic here
        else:
            click.echo("❌ Fix rejected by human")
            
if __name__ == "__main__":
    debug_with_ai()
```

### 3.3 Error Capture Middleware
```python
# error_capture.py
from flask import Flask, request, jsonify
import traceback
import json
from datetime import datetime

class ErrorCaptureMiddleware:
    def __init__(self, app):
        self.app = app
        self.app.before_request(self.before_request)
        self.app.after_request(self.after_request)
        self.app.errorhandler(Exception)(self.handle_error)
        
    def before_request(self):
        """Capture request context"""
        request.start_time = datetime.now()
        
    def after_request(self, response):
        """Log successful requests"""
        duration = (datetime.now() - request.start_time).total_seconds()
        if response.status_code >= 400:
            self.capture_error_context(response)
        return response
        
    def handle_error(self, error):
        """Capture all errors with context"""
        error_context = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": request.endpoint,
            "method": request.method,
            "url": request.url,
            "headers": dict(request.headers),
            "body": request.get_json(silent=True),
            "error": str(error),
            "traceback": traceback.format_exc(),
            "session_data": dict(session) if 'session' in globals() else {}
        }
        
        # Save for AI analysis
        with open(f"errors/error_{datetime.now().timestamp()}.json", "w") as f:
            json.dump(error_context, f, indent=2)
            
        return jsonify({"error": "Internal server error", "id": error_context["timestamp"]}), 500
```

## 📋 Implementation Checklist

### Pre-Setup
- [ ] Backup existing project
- [ ] Create new branch: `git checkout -b feature/three-tier-setup`
- [ ] Review current dependencies in requirements.txt

### Phase 1: Docker Environment
- [ ] Create Dockerfile
- [ ] Create docker-compose.yml
- [ ] Create .env file with API keys
- [ ] Build Docker images: `docker-compose build`
- [ ] Start services: `docker-compose up -d`
- [ ] Run database initialization
- [ ] Verify services are running

### Phase 2: Diagnostics
- [ ] Create test_diagnostics.py
- [ ] Create test_ui_diagnostics.py
- [ ] Create run_diagnostics.sh
- [ ] Run diagnostic suite
- [ ] Fix any failing tests
- [ ] Document test results

### Phase 3: AI Workflow
- [ ] Create ai_debug_assistant.py
- [ ] Create human_control.py
- [ ] Create error_capture.py
- [ ] Integrate error capture with Flask app
- [ ] Test error capture and AI analysis
- [ ] Create errors/ directory for captures

### Post-Setup Validation
- [ ] Run full diagnostic suite
- [ ] Test AI debugging workflow with sample error
- [ ] Verify human control points work
- [ ] Document setup in README
- [ ] Commit changes

## 🚀 Quick Start Commands

```bash
# Clone and setup
git clone <repo>
cd offer-creator
git checkout -b feature/three-tier-setup

# Docker setup
docker-compose build
docker-compose up -d

# Run diagnostics
./run_diagnostics.sh

# View logs
docker-compose logs -f web

# Interactive debugging
python human_control.py --error-file errors/latest.json
```

## 📊 Success Criteria

1. **Environment**: All services start without errors
2. **Diagnostics**: All tests pass within 30 seconds
3. **AI Integration**: Error analysis provides actionable fixes
4. **Human Control**: No automated fixes without approval
5. **Performance**: Page loads under 2 seconds

## 🔧 Troubleshooting

### Common Issues

1. **Port conflicts**: Change ports in docker-compose.yml
2. **Database errors**: Check PostgreSQL logs with `docker-compose logs db`
3. **AI timeouts**: Verify GEMINI_API_KEY in .env
4. **UI test failures**: Ensure Playwright dependencies installed

### Debug Commands

```bash
# Check service status
docker-compose ps

# View specific service logs
docker-compose logs web
docker-compose logs db

# Execute commands in container
docker-compose exec web python -c "import os; print(os.environ)"

# Reset everything
docker-compose down -v
docker-compose up -d --build
```

## 📝 Notes

- This setup prioritizes debuggability over performance
- All AI suggestions require human approval
- Error contexts are captured but not sent externally
- Docker ensures consistent environment across machines