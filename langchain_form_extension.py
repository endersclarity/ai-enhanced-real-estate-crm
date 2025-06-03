#!/usr/bin/env python3
"""
LangChain Form Generation Extension - AI001
Extend existing Gemini 2.5 Flash LangChain functions with form-specific capabilities
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from form_population_engine import FormPopulationEngine
from crm_field_mapper import CRMFieldMapper

class LangChainFormExtension:
    """Extended LangChain integration for intelligent form generation"""
    
    def __init__(self, api_key: Optional[str] = None):
        # Use the proven working Gemini configuration
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "AIzaSyCJ8-hQJVLGXDkHy2sjw-O6Dls0FVO0gGU")
        
        # Initialize LangChain with exact working pattern
        self.llm = ChatGoogleGenerativeAI(
            model="models/gemini-2.5-flash-preview-04-17",  # WITH "models/" prefix
            google_api_key=self.api_key,
            temperature=0.1
        )
        
        # Initialize form generation components
        self.form_engine = FormPopulationEngine()
        self.field_mapper = CRMFieldMapper()
        
        # Load form generation system prompts
        self.system_prompts = self._initialize_system_prompts()
        
    def _initialize_system_prompts(self) -> Dict[str, str]:
        """Initialize specialized system prompts for form generation"""
        return {
            "form_request_parser": """You are an expert real estate form generation assistant. Your role is to parse natural language requests for real estate forms and extract structured information.

AVAILABLE FORMS:
1. California Residential Purchase Agreement
2. Buyer Representation and Broker Compensation Agreement  
3. Transaction Record
4. Verification of Property Condition
5. Statewide Buyer and Seller Advisory
6. Agent Visual Inspection Disclosure
7. Market Conditions Advisory
8. Electronic Signature Verification for Third Parties
9. Confidentiality and Non-Disclosure Agreement
10. Modification of Terms - Buyer Representation Agreement
11. Addendum to Statewide Buyer and Seller Advisory
12. Septic/Well/Property Monument/Propane Allocation of Cost Addendum
13. Permit Transmittal

TASK: Parse the user's request and return a JSON object with:
- form_type: The specific form type requested
- client_info: Any client/buyer information mentioned
- property_info: Any property information mentioned  
- transaction_details: Any transaction specifics mentioned
- agent_info: Any agent information mentioned
- special_requirements: Any special conditions or requirements

EXAMPLE:
User: "Generate a purchase agreement for John Smith buying 123 Main Street for $500,000"
Response: {
  "form_type": "California Residential Purchase Agreement",
  "client_info": {"buyer_name": "John Smith"},
  "property_info": {"address": "123 Main Street"},
  "transaction_details": {"purchase_price": "$500,000"},
  "agent_info": {},
  "special_requirements": []
}

Be precise and extract all relevant information. If information is missing, indicate it clearly.""",

            "crm_data_matcher": """You are an expert CRM data matching assistant. Your role is to match parsed form requirements with available CRM database records.

TASK: Given form requirements and available CRM data, determine the best matches and identify any missing information.

Return a JSON object with:
- matched_records: Dictionary of matched CRM records by type (client, property, transaction)
- confidence_scores: Confidence level for each match (0-100)
- missing_data: List of required fields that couldn't be matched
- suggestions: Recommendations for completing missing information

Focus on accuracy and provide clear reasoning for matches.""",

            "form_completion_guide": """You are an expert real estate form completion assistant. Your role is to guide users through completing any missing information required for form generation.

TASK: Given a form type and missing data requirements, provide clear, step-by-step guidance for completing the form.

Provide:
- Clear explanations of what information is needed
- Legal requirements and compliance notes
- Suggestions for standard values when appropriate
- Warnings about critical fields that must be completed manually

Be helpful, accurate, and compliance-focused."""
        }
    
    def parse_form_request(self, user_request: str) -> Dict[str, Any]:
        """Parse natural language form generation request"""
        try:
            messages = [
                SystemMessage(content=self.system_prompts["form_request_parser"]),
                HumanMessage(content=f"Parse this form generation request: {user_request}")
            ]
            
            response = self.llm.invoke(messages)
            
            # Parse JSON response
            try:
                parsed_request = json.loads(response.content)
                parsed_request["original_request"] = user_request
                parsed_request["parsed_at"] = datetime.now().isoformat()
                return parsed_request
            except json.JSONDecodeError:
                # Fallback if response isn't valid JSON
                return {
                    "error": "Could not parse AI response as JSON",
                    "raw_response": response.content,
                    "original_request": user_request
                }
                
        except Exception as e:
            return {
                "error": f"Failed to parse form request: {str(e)}",
                "original_request": user_request
            }
    
    def match_crm_data(self, parsed_request: Dict[str, Any]) -> Dict[str, Any]:
        """Match parsed request with available CRM data"""
        try:
            # Extract search criteria from parsed request
            search_criteria = self._extract_search_criteria(parsed_request)
            
            # Search CRM for matching records
            matched_records = self._search_crm_records(search_criteria)
            
            # Use AI to evaluate matches and suggest completions
            match_evaluation = self._evaluate_matches_with_ai(parsed_request, matched_records)
            
            return {
                "success": True,
                "search_criteria": search_criteria,
                "matched_records": matched_records,
                "ai_evaluation": match_evaluation,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to match CRM data: {str(e)}",
                "parsed_request": parsed_request
            }
    
    def generate_form_with_ai_guidance(self, form_request: Dict[str, Any], 
                                     crm_matches: Dict[str, Any]) -> Dict[str, Any]:
        """Generate form with AI guidance for missing data"""
        try:
            # Determine best transaction ID from matches
            transaction_id = self._determine_transaction_id(crm_matches)
            
            if not transaction_id:
                # Create guidance for manual data entry
                guidance = self._generate_completion_guidance(form_request, crm_matches)
                return {
                    "success": False,
                    "requires_manual_completion": True,
                    "guidance": guidance,
                    "crm_matches": crm_matches
                }
            
            # Attempt form generation
            form_type = self._map_form_type(form_request.get("form_type", ""))
            result = self.form_engine.populate_form(transaction_id, form_type)
            
            if result.get("success"):
                # Add AI-generated completion notes
                completion_notes = self._generate_completion_notes(form_request, result)
                result["ai_completion_notes"] = completion_notes
                return result
            else:
                # Handle form generation errors with AI guidance
                error_guidance = self._generate_error_guidance(result, form_request)
                result["ai_error_guidance"] = error_guidance
                return result
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Form generation failed: {str(e)}",
                "form_request": form_request
            }
    
    def process_natural_language_form_request(self, user_request: str) -> Dict[str, Any]:
        """Complete end-to-end processing of natural language form request"""
        try:
            print(f"🤖 Processing natural language form request...")
            
            # Step 1: Parse the request
            print("📝 Parsing form request...")
            parsed_request = self.parse_form_request(user_request)
            
            if "error" in parsed_request:
                return parsed_request
            
            # Step 2: Match with CRM data
            print("🔍 Matching with CRM data...")
            crm_matches = self.match_crm_data(parsed_request)
            
            if not crm_matches.get("success"):
                return crm_matches
            
            # Step 3: Generate form with AI guidance
            print("📄 Generating form with AI guidance...")
            form_result = self.generate_form_with_ai_guidance(parsed_request, crm_matches)
            
            # Step 4: Provide comprehensive response
            return {
                "success": form_result.get("success", False),
                "original_request": user_request,
                "parsed_request": parsed_request,
                "crm_matches": crm_matches,
                "form_generation_result": form_result,
                "ai_processing_complete": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Natural language processing failed: {str(e)}",
                "original_request": user_request
            }
    
    def _extract_search_criteria(self, parsed_request: Dict[str, Any]) -> Dict[str, Any]:
        """Extract search criteria from parsed request"""
        criteria = {}
        
        # Extract client search terms
        client_info = parsed_request.get("client_info", {})
        if client_info:
            criteria["client"] = client_info
        
        # Extract property search terms
        property_info = parsed_request.get("property_info", {})
        if property_info:
            criteria["property"] = property_info
        
        # Extract transaction search terms
        transaction_details = parsed_request.get("transaction_details", {})
        if transaction_details:
            criteria["transaction"] = transaction_details
        
        return criteria
    
    def _search_crm_records(self, search_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Search CRM database for matching records"""
        # This would integrate with the actual CRM database
        # For now, return sample matches structure
        return {
            "clients": [],
            "properties": [], 
            "transactions": [],
            "agents": []
        }
    
    def _evaluate_matches_with_ai(self, parsed_request: Dict[str, Any], 
                                matched_records: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to evaluate CRM matches and provide recommendations"""
        try:
            evaluation_prompt = f"""
            Evaluate these CRM search results for form generation:
            
            Request: {json.dumps(parsed_request, indent=2)}
            Matches: {json.dumps(matched_records, indent=2)}
            
            Provide evaluation in JSON format with:
            - best_matches: Most likely correct records
            - confidence_scores: 0-100 for each match type
            - missing_information: What data is still needed
            - recommendations: Next steps for completion
            """
            
            messages = [
                SystemMessage(content=self.system_prompts["crm_data_matcher"]),
                HumanMessage(content=evaluation_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            try:
                return json.loads(response.content)
            except json.JSONDecodeError:
                return {
                    "evaluation_failed": True,
                    "raw_response": response.content
                }
                
        except Exception as e:
            return {
                "evaluation_error": str(e)
            }
    
    def _determine_transaction_id(self, crm_matches: Dict[str, Any]) -> Optional[str]:
        """Determine best transaction ID from CRM matches"""
        # Implementation would analyze matches and return best transaction ID
        # For now, return None to trigger manual completion flow
        return None
    
    def _generate_completion_guidance(self, form_request: Dict[str, Any], 
                                    crm_matches: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI guidance for completing missing form data"""
        try:
            guidance_prompt = f"""
            Provide step-by-step guidance for completing this form request:
            
            Form Request: {json.dumps(form_request, indent=2)}
            Available Data: {json.dumps(crm_matches, indent=2)}
            
            Provide guidance in JSON format with:
            - required_fields: List of fields that must be completed
            - optional_fields: Fields that can be left blank
            - legal_requirements: Important legal considerations
            - step_by_step_guide: Clear instructions for completion
            - estimated_time: How long completion should take
            """
            
            messages = [
                SystemMessage(content=self.system_prompts["form_completion_guide"]),
                HumanMessage(content=guidance_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            try:
                return json.loads(response.content)
            except json.JSONDecodeError:
                return {
                    "guidance_failed": True,
                    "raw_response": response.content
                }
                
        except Exception as e:
            return {
                "guidance_error": str(e)
            }
    
    def _generate_completion_notes(self, form_request: Dict[str, Any], 
                                 form_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI completion notes for successfully generated form"""
        try:
            notes_prompt = f"""
            Provide completion notes for this successfully generated form:
            
            Original Request: {json.dumps(form_request, indent=2)}
            Generation Result: {json.dumps(form_result, indent=2)}
            
            Provide notes in JSON format with:
            - completion_summary: What was successfully populated
            - review_recommendations: What the user should verify
            - next_steps: Recommended actions after form generation
            - compliance_notes: Any legal or compliance considerations
            """
            
            messages = [
                SystemMessage(content="You are an expert real estate form completion assistant providing post-generation guidance."),
                HumanMessage(content=notes_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            try:
                return json.loads(response.content)
            except json.JSONDecodeError:
                return {
                    "notes_failed": True,
                    "raw_response": response.content
                }
                
        except Exception as e:
            return {
                "notes_error": str(e)
            }
    
    def _generate_error_guidance(self, form_result: Dict[str, Any], 
                               form_request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI guidance for form generation errors"""
        try:
            error_prompt = f"""
            Provide helpful guidance for this form generation error:
            
            Error Result: {json.dumps(form_result, indent=2)}
            Original Request: {json.dumps(form_request, indent=2)}
            
            Provide guidance in JSON format with:
            - error_explanation: Clear explanation of what went wrong
            - possible_causes: Likely reasons for the error
            - resolution_steps: Step-by-step instructions to resolve
            - alternative_approaches: Other ways to accomplish the task
            """
            
            messages = [
                SystemMessage(content="You are an expert troubleshooting assistant for real estate form generation."),
                HumanMessage(content=error_prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            try:
                return json.loads(response.content)
            except json.JSONDecodeError:
                return {
                    "guidance_failed": True,
                    "raw_response": response.content
                }
                
        except Exception as e:
            return {
                "guidance_error": str(e)
            }
    
    def _map_form_type(self, form_type_string: str) -> str:
        """Map natural language form type to system form type"""
        form_mapping = {
            "california residential purchase agreement": "california_residential_purchase_agreement",
            "purchase agreement": "california_residential_purchase_agreement",
            "buyer representation": "buyer_representation_agreement",
            "transaction record": "transaction_record",
            "property condition": "property_condition_verification"
        }
        
        form_type_lower = form_type_string.lower()
        
        for key, value in form_mapping.items():
            if key in form_type_lower:
                return value
        
        # Default to purchase agreement
        return "california_residential_purchase_agreement"

def main():
    """Test the LangChain form extension"""
    print("🚀 LangChain Form Extension - AI001")
    print("=" * 50)
    
    # Test with sample requests
    extension = LangChainFormExtension()
    
    test_requests = [
        "Generate a purchase agreement for John Smith buying 123 Main Street for $500,000",
        "Create a buyer representation agreement for Jane Doe",
        "I need a transaction record for the Martinez property sale",
        "Generate a property condition verification form for 456 Oak Avenue"
    ]
    
    print("\n🧪 Testing natural language form processing:")
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n📋 Test {i}: {request}")
        
        # Test just the parsing component (full processing requires CRM data)
        parsed = extension.parse_form_request(request)
        
        if "error" not in parsed:
            print(f"   ✅ Parsed successfully")
            print(f"   📄 Form Type: {parsed.get('form_type', 'Unknown')}")
            print(f"   👤 Client Info: {parsed.get('client_info', {})}")
            print(f"   🏠 Property Info: {parsed.get('property_info', {})}")
        else:
            print(f"   ❌ Parsing failed: {parsed['error']}")
    
    print(f"\n✅ AI001 Complete: LangChain Form Extension")
    print(f"🔄 Ready for natural language form generation integration")

if __name__ == "__main__":
    main()