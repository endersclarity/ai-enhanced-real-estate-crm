#!/usr/bin/env python3
"""
Quick AI Agent Test - See what our enhanced AI can do
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_ai_capabilities():
    """Test the AI agent without needing the web server"""
    print("🤖 Testing Enhanced AI CRM Agent")
    print("=" * 50)
    
    # Import our enhanced functions
    from real_estate_crm import get_available_functions, build_ai_context, get_gemini_response
    
    # Show what functions the AI knows about
    functions = get_available_functions()
    print(f"📊 AI knows about {len(functions)} CRM functions:")
    
    # Show some key functions
    key_functions = ['create_zipform_client', 'find_mls_property', 'create_zipform_transaction', 'find_contacts']
    for func_name in key_functions:
        if func_name in functions:
            func_info = functions[func_name]
            print(f"  ✅ {func_name}: {func_info.get('description', 'No description')}")
        else:
            print(f"  ❌ {func_name}: Not available")
    
    print(f"\n🧠 AI Context Preview:")
    context = build_ai_context()
    print(f"📏 Context length: {len(context)} characters")
    print(f"📝 Context preview:\n{context[:400]}...\n")
    
    # Test AI responses (these will work even without API key - it'll show what it WOULD do)
    test_scenarios = [
        "I have a new buyer client named Sarah Johnson, email sarah@email.com",
        "Can you look up MLS #223040162?", 
        "I need to create an offer for 123 Main Street"
    ]
    
    print("🎯 AI Response Testing:")
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. Testing: {scenario}")
        
        try:
            # This will return enhanced response format even if API fails
            result = get_gemini_response(scenario)
            
            if isinstance(result, dict):
                print(f"   🤖 AI would respond with enhanced features")
                print(f"   📊 Confidence: {result.get('confidence', 0.0):.2f}")
                print(f"   🔧 Function suggestions: {len(result.get('suggested_functions', []))}")
                
                # Show function suggestions
                for suggestion in result.get('suggested_functions', []):
                    print(f"       → {suggestion.get('function')}: {suggestion.get('reason')}")
            else:
                print(f"   🤖 Basic response: {result[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print(f"\n✅ Enhanced AI Agent is ready!")
    print(f"🌐 To test in browser, visit: http://172.22.206.209:5000")
    print(f"💬 The AI chatbot sidebar will suggest database operations automatically")

if __name__ == "__main__":
    test_ai_capabilities()