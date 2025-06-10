#!/usr/bin/env python3
"""
Tier 3: Human-in-the-loop control interface
Ensures no AI fix is applied without human review and approval
"""
import json
import os
import subprocess
from typing import Dict, Any, List
from local_ai_analyzer import LocalAIAnalyzer
# Simple color codes without colorama
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

Fore = Colors
Style = type('Style', (), {'RESET_ALL': Colors.ENDC})

class HumanControlInterface:
    def __init__(self):
        self.analyzer = LocalAIAnalyzer()
        
    def display_fix(self, fix: Dict[str, Any]):
        """Display fix in human-readable format"""
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}🔧 PROPOSED FIX{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        print(f"\nFix Type: {Fore.GREEN}{fix.get('fix_type', 'unknown')}{Style.RESET_ALL}")
        
        if 'changes' in fix and fix['changes']:
            print(f"\n{Fore.YELLOW}📝 Code Changes:{Style.RESET_ALL}")
            for i, change in enumerate(fix['changes'], 1):
                print(f"\n  Change #{i}:")
                print(f"  File: {Fore.BLUE}{change.get('file', 'unknown')}{Style.RESET_ALL}")
                if 'line' in change:
                    print(f"  Line: {change['line']}")
                if 'old' in change:
                    print(f"  {Fore.RED}- Remove:{Style.RESET_ALL}")
                    print("    " + change['old'].replace('\n', '\n    '))
                if 'new' in change:
                    print(f"  {Fore.GREEN}+ Add:{Style.RESET_ALL}")
                    print("    " + change['new'].replace('\n', '\n    '))
                    
        if 'commands' in fix and fix['commands']:
            print(f"\n{Fore.YELLOW}🖥️  Commands to Run:{Style.RESET_ALL}")
            for cmd in fix['commands']:
                print(f"  $ {Fore.CYAN}{cmd}{Style.RESET_ALL}")
                
        if 'verification' in fix:
            print(f"\n{Fore.YELLOW}✅ Verification:{Style.RESET_ALL}")
            print(f"  {fix['verification']}")
            
    def get_user_approval(self, fix: Dict[str, Any], validation: Dict[str, Any]) -> bool:
        """Get explicit user approval before applying fix"""
        
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⚖️  HUMAN APPROVAL REQUIRED{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        if not validation['safe']:
            print(f"\n{Fore.RED}⚠️  WARNING: This fix has potential risks!{Style.RESET_ALL}")
            for risk in validation['risks']:
                print(f"  • {risk}")
                
        if validation['warnings']:
            print(f"\n{Fore.YELLOW}📋 Warnings:{Style.RESET_ALL}")
            for warning in validation['warnings']:
                print(f"  • {warning}")
                
        print(f"\n{Fore.CYAN}Do you want to:{Style.RESET_ALL}")
        print("  1. Apply this fix automatically")
        print("  2. Apply manually (show commands)")
        print("  3. Modify the fix")
        print("  4. Reject and try different approach")
        print("  5. Exit without applying")
        
        while True:
            choice = input(f"\n{Fore.GREEN}Your choice (1-5): {Style.RESET_ALL}").strip()
            if choice in ['1', '2', '3', '4', '5']:
                return choice
            print(f"{Fore.RED}Invalid choice. Please enter 1-5.{Style.RESET_ALL}")
            
    def apply_code_changes(self, changes: List[Dict[str, Any]]) -> bool:
        """Apply code changes with backup"""
        success = True
        backups = []
        
        for change in changes:
            file_path = change.get('file', '')
            if not os.path.exists(file_path):
                print(f"{Fore.RED}❌ File not found: {file_path}{Style.RESET_ALL}")
                success = False
                continue
                
            # Create backup
            backup_path = f"{file_path}.backup"
            subprocess.run(f"cp {file_path} {backup_path}", shell=True)
            backups.append((file_path, backup_path))
            print(f"{Fore.GREEN}✅ Backup created: {backup_path}{Style.RESET_ALL}")
            
            try:
                # Read file
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                # Apply change
                if 'old' in change and 'new' in change:
                    if change['old'] in content:
                        content = content.replace(change['old'], change['new'])
                        print(f"{Fore.GREEN}✅ Replaced content in {file_path}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.YELLOW}⚠️  Old content not found in {file_path}{Style.RESET_ALL}")
                        success = False
                        
                # Write file
                with open(file_path, 'w') as f:
                    f.write(content)
                    
            except Exception as e:
                print(f"{Fore.RED}❌ Error modifying {file_path}: {e}{Style.RESET_ALL}")
                success = False
                
        return success, backups
        
    def run_commands(self, commands: List[str]) -> bool:
        """Run shell commands with output capture"""
        success = True
        
        for cmd in commands:
            print(f"\n{Fore.CYAN}$ {cmd}{Style.RESET_ALL}")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(f"{Fore.YELLOW}{result.stderr}{Style.RESET_ALL}")
                
            if result.returncode != 0:
                print(f"{Fore.RED}❌ Command failed with exit code {result.returncode}{Style.RESET_ALL}")
                success = False
            else:
                print(f"{Fore.GREEN}✅ Command completed successfully{Style.RESET_ALL}")
                
        return success
        
    def interactive_debug_session(self, session_path: str):
        """Run interactive debugging session"""
        
        # Load error context
        context_file = os.path.join(session_path, "error_context.json")
        with open(context_file, 'r') as f:
            error_context = json.load(f)
            
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}🤖 HUMAN-IN-THE-LOOP AI DEBUGGING{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"\nError: {error_context['error_description']}")
        print(f"Session: {session_path}")
        
        # Get AI analysis
        print(f"\n{Fore.YELLOW}🔍 Getting AI analysis...{Style.RESET_ALL}")
        analysis = self.assistant.analyze_error(error_context)
        
        print(f"\n{Fore.CYAN}📋 AI Analysis:{Style.RESET_ALL}")
        print(analysis)
        
        # Get fix suggestion
        print(f"\n{Fore.YELLOW}💡 Generating fix...{Style.RESET_ALL}")
        fix = self.assistant.suggest_fix(analysis, error_context)
        
        if 'error' in fix:
            print(f"{Fore.RED}❌ Error generating fix: {fix['error']}{Style.RESET_ALL}")
            return
            
        # Validate fix
        validation = self.assistant.validate_fix(fix)
        
        # Display fix
        self.display_fix(fix)
        
        # Get user approval
        choice = self.get_user_approval(fix, validation)
        
        if choice == '1':  # Apply automatically
            print(f"\n{Fore.YELLOW}🚀 Applying fix...{Style.RESET_ALL}")
            
            # Apply code changes
            if 'changes' in fix and fix['changes']:
                success, backups = self.apply_code_changes(fix['changes'])
                if not success:
                    print(f"{Fore.RED}❌ Some changes failed{Style.RESET_ALL}")
                    
            # Run commands
            if 'commands' in fix and fix['commands']:
                success = self.run_commands(fix['commands'])
                
            # Verify fix
            if success and 'verification' in fix:
                print(f"\n{Fore.YELLOW}✅ Verifying fix...{Style.RESET_ALL}")
                print(f"Run: {fix['verification']}")
                
        elif choice == '2':  # Manual application
            print(f"\n{Fore.YELLOW}📋 Manual Application Instructions:{Style.RESET_ALL}")
            
            if 'changes' in fix:
                for i, change in enumerate(fix['changes'], 1):
                    print(f"\nStep {i}: Edit {change['file']}")
                    if 'line' in change:
                        print(f"  Go to line {change['line']}")
                    if 'old' in change:
                        print(f"  Find: {change['old']}")
                    if 'new' in change:
                        print(f"  Replace with: {change['new']}")
                        
            if 'commands' in fix:
                print("\nThen run these commands:")
                for cmd in fix['commands']:
                    print(f"  $ {cmd}")
                    
        elif choice == '3':  # Modify fix
            print(f"{Fore.YELLOW}Fix modification not implemented yet{Style.RESET_ALL}")
            
        elif choice == '4':  # Different approach
            print(f"{Fore.YELLOW}Requesting alternative approach...{Style.RESET_ALL}")
            
        else:  # Exit
            print(f"{Fore.YELLOW}Exiting without applying fix{Style.RESET_ALL}")
            

if __name__ == "__main__":
    import sys
    
    interface = HumanControlInterface()
    
    if len(sys.argv) > 1:
        session_path = sys.argv[1]
    else:
        # Find most recent session
        sessions = sorted(os.listdir("ai-debug/sessions"))
        if sessions:
            session_path = os.path.join("ai-debug/sessions", sessions[-1])
        else:
            print("No debug sessions found. Run capture_error.py first.")
            sys.exit(1)
            
    interface.interactive_debug_session(session_path)