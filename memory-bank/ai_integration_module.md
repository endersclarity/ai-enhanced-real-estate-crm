# Module: AI Integration

## Purpose & Responsibility
Provides intelligent automation through Google Gemini 2.5 Flash AI with LangChain function calling, enabling natural language CRM operations, email content extraction, and form generation requests. Implements secure AI-to-database operations with mandatory user confirmation and comprehensive audit logging.

## Interfaces
* `AIAssistant`: Main AI conversation interface
  * `process_chat_message()`: Handle natural language queries and commands
  * `extract_email_content()`: Parse emails for client/property/transaction data
  * `propose_database_operation()`: Generate database operations with user preview
  * `confirm_and_execute()`: Execute approved operations with audit logging
* `FunctionCalling`: LangChain integration for structured operations
  * `add_client_tool()`: AI-assisted client creation with validation
  * `search_properties_tool()`: Natural language property queries
  * `generate_form_tool()`: AI-triggered form generation requests
* Input: Natural language text, email content, voice commands
* Output: Structured operation proposals, database confirmations, AI responses

## Implementation Details
* Files:
  * `ai_chatbot_integration.py` - Main AI conversation processing engine
  * `core_app/zipform_ai_functions.py` - LangChain function calling implementations
  * `core_app/ai_modules/ai_instruction_framework.js` - Client-side AI interaction
  * `core_app/ai_modules/offer_creation_functions.py` - Real estate specific AI tools
* Important algorithms:
  * Natural language to structured database operation conversion
  * Email entity extraction with confidence scoring
  * Context-aware conversation memory with session management
  * Security-first AI operations requiring explicit user approval
* Data Models:
  * `AIConversation` - Chat history and context preservation
  * `OperationProposal` - AI-generated database operation previews
  * `ConfirmationWorkflow` - User approval tracking and audit trails

## Current Implementation Status
* Completed: Gemini 2.5 Flash integration, LangChain function calling, email processing, conversation memory
* In Progress: **PARTIALLY FUNCTIONAL** - Core AI features working but blocked by CRM database issues
* Pending: Form generation AI tools, advanced natural language query capabilities

## Implementation Plans & Tasks
* `implementation_plan_ai_crm_integration.md`
  * [Database Connection]: Fix AI tools connection to corrected CRM schema
  * [Function Expansion]: Add comprehensive real estate operation tools
  * [Error Handling]: Improve AI response quality for database operation failures
* `implementation_plan_ai_form_generation.md`
  * [Form AI Tools]: Integrate AI with form processing module
  * [Natural Language Forms]: Enable \"Create purchase agreement for client X property Y\"
  * [Template Selection]: AI-assisted form type and template selection

## Mini Dependency Tracker
---mini_tracker_start---
Dependencies:
- crm_core_module.md (requires functional CRM database for AI operations)
- form_processing_module.md (for AI-triggered form generation)

Dependents:
- Primary user interface for non-technical CRM operations
- Email automation and data extraction workflows
- Natural language form generation capabilities
- Business process automation objectives
---mini_tracker_end---
