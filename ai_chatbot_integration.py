#!/usr/bin/env python3
"""
AI Chatbot Integration for Form Generation
Task #8: Integrate with AI Chatbot for Natural Language Requests

Extends the existing LangChain/Gemini 2.5 Flash chatbot to understand 
natural language form generation requests and process them automatically.
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
import logging

from form_api_backend import FormBackendService
from coordinate_based_form_filler import CoordinateBasedFormFiller

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIFormAssistant:
    """AI-powered form generation assistant using LangChain and Gemini"""
    
    def __init__(self, api_key: str = None):
        """Initialize AI assistant with Gemini integration"""
        
        # Use API key from environment or parameter
        self.api_key = api_key or os.getenv('GEMINI_API_KEY', 'AIzaSyCJ8-hQJVLGXDkHy2sjw-O6Dls0FVO0gGU')
        
        # Initialize LangChain with Gemini 2.5 Flash
        self.llm = ChatGoogleGenerativeAI(
            model="models/gemini-2.5-flash-preview-04-17",
            google_api_key=self.api_key,
            temperature=0.1
        )
        
        # Initialize form backend service and form filler
        self.form_service = FormBackendService()
        self.form_filler = CoordinateBasedFormFiller()
        
        # Define supported intents and patterns
        self.intent_patterns = self._load_intent_patterns()
        
        logger.info("✅ AI Form Assistant initialized with Gemini 2.5 Flash")
    
    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """Load natural language intent patterns for form generation"""
        return {
            'form_generation': [
                r'generate.*(?:purchase agreement|contract)',
                r'create.*(?:form|document|agreement)',
                r'make.*(?:purchase agreement|offer)',
                r'prepare.*(?:contract|paperwork)',
                r'fill out.*(?:form|agreement)',
                r'populate.*(?:document|form)'
            ],
            'form_validation': [
                r'check.*(?:form|document|contract)',
                r'validate.*(?:information|data|form)',
                r'review.*(?:document|contract)',
                r'verify.*(?:form|agreement)'
            ],
            'form_inquiry': [
                r'what.*(?:forms|documents).*(?:need|required)',
                r'which.*(?:form|document).*(?:use|choose)',
                r'show.*(?:available|supported).*forms',
                r'list.*forms'
            ],
            'client_property_extraction': [
                r'for\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # Names
                r'(?:client|buyer|seller)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'(\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln))',  # Addresses
                r'property.*?(\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln))'
            ]
        }
    
    def extract_intent_and_entities(self, user_message: str) -> Dict[str, Any]:
        """Extract intent and entities from user message"""
        
        message_lower = user_message.lower()
        
        # Detect primary intent
        intent = 'unknown'
        confidence = 0.0
        
        for intent_type, patterns in self.intent_patterns.items():
            if intent_type == 'client_property_extraction':
                continue  # Skip entity patterns in intent detection
                
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    intent = intent_type
                    confidence = 0.9
                    break
        
        # Extract entities (names, addresses, form types)
        entities = {
            'client_names': [],
            'property_addresses': [],
            'form_types': [],
            'amounts': [],
            'dates': []
        }
        
        # Extract client names
        name_patterns = [
            r'(?:for|client|buyer|seller)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)(?:\s+and|\s+at|\s+on)'
        ]
        
        for pattern in name_patterns:
            matches = re.finditer(pattern, user_message)
            for match in matches:
                name = match.group(1).strip()
                if len(name.split()) >= 2:  # At least first and last name
                    entities['client_names'].append(name)
        
        # Extract property addresses
        address_patterns = [
            r'(\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Boulevard|Blvd|Lane|Ln))',
            r'(?:property|address|located).*?(\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr))'
        ]
        
        for pattern in address_patterns:
            matches = re.finditer(pattern, user_message, re.IGNORECASE)
            for match in matches:
                address = match.group(1).strip()
                entities['property_addresses'].append(address)
        
        # Extract form types
        form_keywords = {
            'purchase agreement': 'california_purchase_agreement',
            'buyer representation': 'buyer_representation_agreement',
            'transaction record': 'transaction_record',
            'property condition': 'verification_property_condition',
            'advisory': 'statewide_buyer_seller_advisory'
        }
        
        for keyword, form_id in form_keywords.items():
            if keyword in message_lower:
                entities['form_types'].append(form_id)
        
        # Extract monetary amounts
        amount_pattern = r'\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        amounts = re.findall(amount_pattern, user_message)
        entities['amounts'] = [amount.replace(',', '') for amount in amounts]
        
        return {
            'intent': intent,
            'confidence': confidence,
            'entities': entities,
            'original_message': user_message
        }
    
    def generate_ai_response(self, user_message: str, context: Dict[str, Any]) -> str:
        """Generate AI response using LangChain and Gemini"""
        
        # Create system prompt for form generation assistant
        system_prompt = """You are an expert real estate form generation assistant for Narissa Realty. 

Your capabilities:
- Generate California Association of Realtors (CAR) forms
- Validate form data and requirements
- Extract client and property information from natural language
- Provide guidance on required forms and documentation

Available forms:
1. California Residential Purchase Agreement (27 pages) - Main purchase contract
2. Buyer Representation Agreement (13 pages) - Agent representation contract  
3. Transaction Record (3 pages) - Transaction documentation
4. Verification of Property Condition (1 page) - Property disclosure
5. Statewide Buyer and Seller Advisory (15 pages) - Required advisory

When users request form generation:
1. Identify the specific form needed
2. Extract client/property information from their request
3. Confirm missing required information
4. Proceed with form generation if sufficient data available
5. Provide clear next steps and document download information

Be helpful, professional, and ensure legal compliance. Always confirm critical details before generating forms."""

        # Create user message with context
        enhanced_message = f"""
User Request: {user_message}

Extracted Context:
- Intent: {context['intent']}
- Client Names: {context['entities']['client_names']}
- Property Addresses: {context['entities']['property_addresses']}
- Form Types: {context['entities']['form_types']}
- Amounts: {context['entities']['amounts']}

Please respond appropriately based on the user's request and extracted information.
"""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=enhanced_message)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"❌ AI response generation failed: {e}")
            return f"I apologize, but I encountered an error processing your request. Please try again or contact support. Error: {str(e)}"
    
    def process_form_generation_request(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Process form generation based on extracted entities"""
        
        # Default to purchase agreement if no specific form mentioned
        form_type = entities['form_types'][0] if entities['form_types'] else 'california_purchase_agreement'
        
        # Try to match client names to CRM data (mock for now)
        client_id = self._resolve_client_id(entities['client_names'])
        property_id = self._resolve_property_id(entities['property_addresses'])
        
        if not client_id:
            return {
                'success': False,
                'error': 'Unable to identify client in CRM database',
                'suggestions': f"Available clients: John Smith, Jane Doe, Robert Johnson"
            }
        
        if not property_id:
            return {
                'success': False, 
                'error': 'Unable to identify property in CRM database',
                'suggestions': f"Available properties: 456 Oak Avenue, 789 Pine Street, 321 Elm Drive"
            }
        
        # Generate the form
        try:
            result = self.form_service.populate_form_request(
                form_id=form_type,
                client_id=client_id,
                property_id=property_id,
                transaction_id='auto_generated'
            )
            
            return {
                'success': True,
                'form_generated': True,
                'form_type': form_type,
                'client_id': client_id,
                'property_id': property_id,
                'output_file': result.get('output_path'),
                'field_count': result.get('field_count'),
                'validation_errors': result.get('validation_errors', [])
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Form generation failed: {str(e)}'
            }
    
    def _resolve_client_id(self, client_names: List[str]) -> Optional[str]:
        """Resolve client names to CRM client IDs (mock implementation)"""
        # Mock client database
        mock_clients = {
            'john smith': 'client_001',
            'jane doe': 'client_002', 
            'robert johnson': 'client_003',
            'mary wilson': 'client_004'
        }
        
        for name in client_names:
            name_key = name.lower()
            if name_key in mock_clients:
                return mock_clients[name_key]
        
        return None
    
    def _resolve_property_id(self, addresses: List[str]) -> Optional[str]:
        """Resolve addresses to CRM property IDs (mock implementation)"""
        # Mock property database
        mock_properties = {
            '456 oak avenue': 'property_001',
            '789 pine street': 'property_002',
            '321 elm drive': 'property_003',
            '123 main street': 'property_004'
        }
        
        for address in addresses:
            address_key = address.lower()
            for mock_addr, prop_id in mock_properties.items():
                if mock_addr in address_key or address_key in mock_addr:
                    return prop_id
        
        return None
    
    def process_natural_language_request(self, user_message: str) -> Dict[str, Any]:
        """Main method to process natural language form requests"""
        
        logger.info(f"🤖 Processing natural language request: {user_message[:100]}...")
        
        # Extract intent and entities
        context = self.extract_intent_and_entities(user_message)
        
        # Generate AI response
        ai_response = self.generate_ai_response(user_message, context)
        
        # Process based on intent
        action_result = None
        
        if context['intent'] == 'form_generation':
            action_result = self.process_form_generation_request(context['entities'])
        
        elif context['intent'] == 'form_inquiry':
            forms_list = self.form_service.get_forms_list()
            action_result = {
                'success': True,
                'available_forms': forms_list,
                'total_count': len(forms_list)
            }
        
        # Compile complete response
        response = {
            'success': True,
            'user_message': user_message,
            'intent': context['intent'],
            'entities_extracted': context['entities'],
            'ai_response': ai_response,
            'action_taken': context['intent'],
            'action_result': action_result,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ Natural language processing complete: {context['intent']}")
        return response

def test_ai_chatbot_integration():
    """Test AI chatbot integration with various natural language requests"""
    
    print("🤖 Testing AI Chatbot Integration")
    print("=" * 50)
    
    # Initialize assistant
    assistant = AIFormAssistant()
    
    # Test cases
    test_requests = [
        "Generate a purchase agreement for John Smith and 456 Oak Avenue",
        "Create a buyer representation agreement for Jane Doe", 
        "What forms do I need for a real estate transaction?",
        "Make a contract for Robert Johnson buying 789 Pine Street for $850,000",
        "Show me available forms"
    ]
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n🧪 Test {i}: {request}")
        print("-" * 40)
        
        try:
            result = assistant.process_natural_language_request(request)
            
            print(f"✅ Intent: {result['intent']}")
            print(f"🎯 Entities: {result['entities_extracted']}")
            
            if result['action_result']:
                if result['action_result']['success']:
                    print(f"🎉 Action Success: {result['action_taken']}")
                    if 'output_file' in result['action_result']:
                        print(f"📄 Generated File: {result['action_result']['output_file']}")
                else:
                    print(f"❌ Action Failed: {result['action_result']['error']}")
            
            # Show AI response preview
            ai_preview = result['ai_response'][:150] + "..." if len(result['ai_response']) > 150 else result['ai_response']
            print(f"💬 AI Response: {ai_preview}")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print(f"\n🎯 AI Chatbot Integration Ready")
    return True

if __name__ == "__main__":
    test_ai_chatbot_integration()