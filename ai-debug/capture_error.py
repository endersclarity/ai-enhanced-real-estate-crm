#!/usr/bin/env python3
"""
Tier 3: Error capture and context gathering for AI debugging
Captures real errors from the running system
"""
import json
import subprocess
import datetime
import os
from typing import Dict, Any

class ErrorCapture:
    def __init__(self, session_dir: str = "ai-debug/sessions"):
        self.session_dir = session_dir
        self.session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_path = os.path.join(session_dir, self.session_id)
        os.makedirs(self.session_path, exist_ok=True)
        
    def capture_docker_logs(self, lines: int = 100) -> str:
        """Capture recent Docker logs"""
        cmd = f"docker-compose -f docker-compose.dev.yml logs --tail={lines} app"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        log_file = os.path.join(self.session_path, "docker_logs.txt")
        with open(log_file, 'w') as f:
            f.write(result.stdout)
            if result.stderr:
                f.write("\n=== STDERR ===\n")
                f.write(result.stderr)
                
        return result.stdout
        
    def capture_endpoint_error(self, endpoint: str) -> Dict[str, Any]:
        """Capture detailed error from a failing endpoint"""
        import requests
        
        url = f"http://localhost:5000{endpoint}"
        try:
            response = requests.get(url, timeout=5)
            return {
                "url": url,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.text[:1000],  # First 1000 chars
                "error_type": "http_error"
            }
        except Exception as e:
            return {
                "url": url,
                "error_type": "connection_error",
                "exception": str(e)
            }
            
    def capture_file_context(self, file_path: str, error_line: int = None) -> Dict[str, Any]:
        """Capture code context around an error"""
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
                
            context = {
                "file_path": file_path,
                "total_lines": len(lines),
                "error_line": error_line
            }
            
            if error_line:
                # Get 10 lines before and after error
                start = max(0, error_line - 10)
                end = min(len(lines), error_line + 10)
                context["code_context"] = {
                    "start_line": start + 1,
                    "end_line": end,
                    "lines": ''.join(lines[start:end])
                }
            else:
                # Get first 50 lines if no specific error line
                context["code_preview"] = ''.join(lines[:50])
                
            return context
        except Exception as e:
            return {"error": str(e), "file_path": file_path}
            
    def capture_system_state(self) -> Dict[str, Any]:
        """Capture overall system state"""
        state = {
            "timestamp": datetime.datetime.now().isoformat(),
            "session_id": self.session_id
        }
        
        # Docker container status
        cmd = "docker-compose -f docker-compose.dev.yml ps --format json"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            try:
                # Parse each line as JSON
                containers = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        containers.append(json.loads(line))
                state["containers"] = containers
            except:
                state["containers_raw"] = result.stdout
        
        # Database file info
        if os.path.exists("real_estate_crm.db"):
            stat = os.stat("real_estate_crm.db")
            state["database"] = {
                "exists": True,
                "size": stat.st_size,
                "modified": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
        else:
            state["database"] = {"exists": False}
            
        return state
        
    def create_error_context(self, error_description: str, endpoint: str = None) -> Dict[str, Any]:
        """Create comprehensive error context for AI analysis"""
        print(f"📸 Capturing error context for: {error_description}")
        
        context = {
            "error_description": error_description,
            "system_state": self.capture_system_state(),
            "docker_logs": self.capture_docker_logs()
        }
        
        if endpoint:
            context["endpoint_error"] = self.capture_endpoint_error(endpoint)
            
        # Try to extract file and line from Docker logs
        if "File" in context["docker_logs"] and "line" in context["docker_logs"]:
            # Parse Python traceback
            import re
            pattern = r'File "([^"]+)", line (\d+)'
            matches = re.findall(pattern, context["docker_logs"])
            if matches:
                # Get the most recent file/line reference
                file_path, line_num = matches[-1]
                # Convert container path to host path
                file_path = file_path.replace("/app/", "")
                context["code_context"] = self.capture_file_context(file_path, int(line_num))
                
        # Save complete context
        context_file = os.path.join(self.session_path, "error_context.json")
        with open(context_file, 'w') as f:
            json.dump(context, f, indent=2, default=str)
            
        print(f"✅ Error context saved to: {context_file}")
        return context
        

def capture_current_error():
    """Capture the current Client Management 500 error"""
    capture = ErrorCapture()
    
    # Capture the specific error we found
    context = capture.create_error_context(
        error_description="Client Management page returns 500 error",
        endpoint="/clients"
    )
    
    print(f"\n📁 Session ID: {capture.session_id}")
    print(f"📍 Session Path: {capture.session_path}")
    
    # Extract key information for display
    if "endpoint_error" in context:
        print(f"\n🔍 Endpoint Error:")
        print(f"  Status Code: {context['endpoint_error']['status_code']}")
        
    if "code_context" in context:
        print(f"\n📄 Error Location:")
        print(f"  File: {context['code_context']['file_path']}")
        print(f"  Line: {context['code_context']['error_line']}")
        
    return capture.session_path
    

if __name__ == "__main__":
    capture_current_error()