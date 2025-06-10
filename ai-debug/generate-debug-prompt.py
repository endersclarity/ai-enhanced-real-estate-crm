#!/usr/bin/env python3
"""
Generate debugging prompt for Claude Code
This is the corrected workflow - no external AI calls
"""
import os
import sys
import json

# Add the directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from local_ai_analyzer import LocalAIAnalyzer

def main():
    # Get the most recent session if not specified
    if len(sys.argv) > 1:
        session_path = sys.argv[1]
    else:
        sessions_dir = "ai-debug/sessions"
        if os.path.exists(sessions_dir):
            sessions = sorted(os.listdir(sessions_dir))
            if sessions:
                session_path = os.path.join(sessions_dir, sessions[-1])
            else:
                print("❌ No debug sessions found. Run capture_error.py first.")
                sys.exit(1)
        else:
            print("❌ No sessions directory found.")
            sys.exit(1)
    
    print("🎯 CORRECT DEBUGGING WORKFLOW")
    print("=" * 60)
    print("This generates a prompt for YOU to give to Claude Code")
    print("NO external AI is called - Claude Code is the only AI needed")
    print("=" * 60)
    
    # Initialize the local analyzer
    analyzer = LocalAIAnalyzer()
    
    # Generate the prompt
    prompt = analyzer.analyze_error_context(session_path)
    prompt_file = analyzer.save_prompt(session_path, prompt)
    
    print(f"\n✅ Prompt saved to: {prompt_file}")
    print("\n📋 COPY THIS PROMPT TO CLAUDE CODE:")
    print("=" * 60)
    print(prompt)
    print("=" * 60)
    
    print("\n🎯 What happens next:")
    print("1. You copy the prompt above")
    print("2. You paste it to Claude Code (me)")  
    print("3. I analyze with full codebase access")
    print("4. I suggest specific fixes")
    print("5. You review and approve")
    print("\nThis is the superior workflow because I can read ALL files, not just logs!")

if __name__ == "__main__":
    main()