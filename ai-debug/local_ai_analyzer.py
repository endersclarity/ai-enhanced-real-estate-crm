#!/usr/bin/env python3
"""
Local AI Analyzer - Generates prompts for Claude Code
NO EXTERNAL AI CALLS - Just formats context into prompts
"""
import json
import os
from datetime import datetime
from typing import Dict, Any

class LocalAIAnalyzer:
    """
    Analyzes errors locally and generates prompts for Claude Code.
    Does NOT call any external AI services.
    """
    
    def __init__(self):
        self.prompt_template = """
Claude Code, I need you to debug this error in my Real Estate CRM:

**Error Summary:**
{error_description}

**System State:**
- Timestamp: {timestamp}
- Container Status: {container_status}
- Database: {database_status}

**Error Details:**
{error_details}

**Recent Docker Logs:**
```
{docker_logs}
```

**Code Context:**
{code_context}

**What I need:**
1. Analyze this error and identify the root cause
2. Suggest a specific fix with exact code changes
3. Explain any risks or side effects
4. Provide verification steps

You have full access to the codebase. Please read any additional files you need to understand the context better.
"""

    def analyze_error_context(self, session_path: str) -> str:
        """
        Read error context and generate a prompt for Claude Code
        """
        # Load the captured error context
        context_file = os.path.join(session_path, "error_context.json")
        with open(context_file, 'r') as f:
            error_context = json.load(f)
        
        # Format the error details
        error_details = ""
        if 'endpoint_error' in error_context:
            endpoint = error_context['endpoint_error']
            error_details = f"""
- Endpoint: {endpoint.get('url', 'Unknown')}
- Status Code: {endpoint.get('status_code', 'Unknown')}
- Error Type: {endpoint.get('error_type', 'Unknown')}
"""

        # Format container status
        container_status = "Unknown"
        if 'system_state' in error_context and 'containers' in error_context['system_state']:
            containers = error_context['system_state']['containers']
            if containers:
                container = containers[0]
                container_status = f"{container.get('State', 'Unknown')} (Port: {container.get('Ports', 'Unknown')})"

        # Format database status
        database_status = "Unknown"
        if 'system_state' in error_context and 'database' in error_context['system_state']:
            db = error_context['system_state']['database']
            database_status = f"{'Exists' if db.get('exists') else 'Missing'} (Size: {db.get('size', 0)} bytes)"

        # Extract relevant docker logs (last 20 lines with errors)
        docker_logs = error_context.get('docker_logs', '')
        log_lines = docker_logs.split('\n')
        
        # Find error lines and include context
        error_lines = []
        for i, line in enumerate(log_lines):
            if any(keyword in line.lower() for keyword in ['error', 'exception', 'traceback', 'file']):
                # Include 2 lines before and after for context
                start = max(0, i - 2)
                end = min(len(log_lines), i + 3)
                error_lines.extend(log_lines[start:end])
                error_lines.append("...")  # Separator
        
        docker_logs_formatted = '\n'.join(error_lines[-40:])  # Last 40 relevant lines

        # Format code context if available
        code_context = ""
        if 'code_context' in error_context:
            ctx = error_context['code_context']
            code_context = f"""
File: {ctx.get('file_path', 'Unknown')}
Line: {ctx.get('error_line', 'Unknown')}

Code snippet:
```python
{ctx.get('code_context', {}).get('lines', 'No code available')}
```
"""

        # Generate the prompt
        prompt = self.prompt_template.format(
            error_description=error_context.get('error_description', 'Unknown error'),
            timestamp=error_context.get('system_state', {}).get('timestamp', 'Unknown'),
            container_status=container_status,
            database_status=database_status,
            error_details=error_details,
            docker_logs=docker_logs_formatted,
            code_context=code_context
        )
        
        return prompt

    def save_prompt(self, session_path: str, prompt: str) -> str:
        """
        Save the generated prompt to a file
        """
        prompt_file = os.path.join(session_path, "claude_code_prompt.txt")
        with open(prompt_file, 'w') as f:
            f.write(prompt)
        
        return prompt_file


def main():
    """
    Main entry point - generate prompt from error context
    """
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python local-ai-analyzer.py <session_path>")
        sys.exit(1)
    
    session_path = sys.argv[1]
    
    if not os.path.exists(session_path):
        print(f"Error: Session path '{session_path}' does not exist")
        sys.exit(1)
    
    analyzer = LocalAIAnalyzer()
    
    print("🔍 Local AI Analyzer")
    print("=" * 50)
    print(f"Session: {session_path}")
    
    # Generate the prompt
    prompt = analyzer.analyze_error_context(session_path)
    
    # Save it
    prompt_file = analyzer.save_prompt(session_path, prompt)
    
    print(f"\n✅ Prompt generated and saved to: {prompt_file}")
    print("\n📋 Generated Prompt Preview:")
    print("-" * 50)
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
    print("-" * 50)
    print("\n🎯 Next Steps:")
    print("1. Copy the prompt above")
    print("2. Paste it to Claude Code")
    print("3. Let Claude Code analyze with full codebase access")
    print("4. Review and approve any suggested fixes")
    
    return prompt_file


if __name__ == "__main__":
    main()