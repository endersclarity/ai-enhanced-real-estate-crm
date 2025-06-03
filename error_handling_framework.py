#!/usr/bin/env python3
"""
Form Population Error Handling & Recovery Framework - ENGINE003
Comprehensive error handling for robust form population with graceful degradation
"""

import logging
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple
from enum import Enum
import json

class ErrorSeverity(Enum):
    """Error severity levels for form population"""
    CRITICAL = "critical"      # Cannot generate form
    WARNING = "warning"        # Form can be generated with missing data
    INFO = "info"             # Minor issues, form quality not affected

class ErrorCategory(Enum):
    """Categories of errors in form population"""
    CRM_DATA = "crm_data"           # Missing/invalid CRM data
    FORM_TEMPLATE = "form_template"  # Template loading/parsing issues
    FIELD_MAPPING = "field_mapping"  # Mapping configuration problems  
    PDF_GENERATION = "pdf_generation" # PDF creation failures
    VALIDATION = "validation"        # Form validation failures
    SYSTEM = "system"               # System-level errors

class FormPopulationError(Exception):
    """Custom exception for form population errors with rich context"""
    
    def __init__(self, message: str, category: ErrorCategory, severity: ErrorSeverity, 
                 context: Optional[Dict[str, Any]] = None, recovery_suggestions: Optional[List[str]] = None):
        super().__init__(message)
        self.category = category
        self.severity = severity
        self.context = context or {}
        self.recovery_suggestions = recovery_suggestions or []
        self.timestamp = datetime.now()

class ErrorHandlingFramework:
    """Comprehensive error handling and recovery system for form population"""
    
    def __init__(self, log_level: str = "INFO"):
        self.logger = self._setup_logging(log_level)
        self.error_history: List[Dict[str, Any]] = []
        self.recovery_strategies = self._initialize_recovery_strategies()
        
    def _setup_logging(self, level: str) -> logging.Logger:
        """Configure logging for error tracking"""
        logger = logging.getLogger("FormPopulationEngine")
        logger.setLevel(getattr(logging, level))
        
        # Create console handler
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _initialize_recovery_strategies(self) -> Dict[ErrorCategory, List[str]]:
        """Define recovery strategies for each error category"""
        return {
            ErrorCategory.CRM_DATA: [
                "Use default placeholder values for missing non-critical fields",
                "Prompt user for manual data entry",
                "Generate partial form with clearly marked missing data sections",
                "Use data from similar transactions as fallback"
            ],
            ErrorCategory.FORM_TEMPLATE: [
                "Fall back to generic template coordinates",
                "Use manual form generation with user guidance",
                "Create simplified version of the form",
                "Download fresh template from official CAR sources"
            ],
            ErrorCategory.FIELD_MAPPING: [
                "Use fuzzy matching for field names",
                "Apply default mapping rules",
                "Generate mapping suggestions for manual review",
                "Skip unmappable fields with warnings"
            ],
            ErrorCategory.PDF_GENERATION: [
                "Retry with simplified formatting",
                "Generate HTML version instead of PDF",
                "Use alternative PDF library (fpdf instead of reportlab)",
                "Create text-based form summary"
            ],
            ErrorCategory.VALIDATION: [
                "Generate form with validation warnings attached",
                "Provide validation checklist for manual review", 
                "Create draft version requiring agent approval",
                "Use relaxed validation rules for edge cases"
            ],
            ErrorCategory.SYSTEM: [
                "Retry operation after brief delay",
                "Check system resources and dependencies",
                "Fall back to manual process with error report",
                "Contact system administrator with diagnostic data"
            ]
        }
    
    def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Main error handling entry point with intelligent recovery"""
        
        # Convert to FormPopulationError if needed
        if not isinstance(error, FormPopulationError):
            form_error = self._classify_error(error, context)
        else:
            form_error = error
        
        # Log the error
        self._log_error(form_error, context)
        
        # Record in error history
        self._record_error(form_error, context)
        
        # Attempt recovery
        recovery_result = self._attempt_recovery(form_error, context)
        
        return {
            "error_handled": True,
            "original_error": str(form_error),
            "error_category": form_error.category.value,
            "error_severity": form_error.severity.value,
            "recovery_attempted": recovery_result["attempted"],
            "recovery_successful": recovery_result["successful"],
            "recovery_method": recovery_result.get("method"),
            "user_action_required": recovery_result.get("user_action_required", False),
            "suggestions": form_error.recovery_suggestions,
            "timestamp": form_error.timestamp.isoformat(),
            "context": context
        }
    
    def _classify_error(self, error: Exception, context: Dict[str, Any]) -> FormPopulationError:
        """Classify generic exceptions into FormPopulationError with context"""
        
        error_str = str(error).lower()
        
        # CRM Data errors
        if any(keyword in error_str for keyword in ["no such table", "database", "sql", "connection"]):
            return FormPopulationError(
                message=f"CRM database error: {str(error)}",
                category=ErrorCategory.CRM_DATA,
                severity=ErrorSeverity.CRITICAL,
                context=context,
                recovery_suggestions=["Check database connection", "Verify database file exists", "Check database schema"]
            )
        
        # Form Template errors
        elif any(keyword in error_str for keyword in ["template", "json", "file not found", "coordinates"]):
            return FormPopulationError(
                message=f"Form template error: {str(error)}",
                category=ErrorCategory.FORM_TEMPLATE,
                severity=ErrorSeverity.WARNING,
                context=context,
                recovery_suggestions=["Verify template file exists", "Check template format", "Use fallback template"]
            )
        
        # PDF Generation errors
        elif any(keyword in error_str for keyword in ["reportlab", "pdf", "canvas", "font"]):
            return FormPopulationError(
                message=f"PDF generation error: {str(error)}",
                category=ErrorCategory.PDF_GENERATION,
                severity=ErrorSeverity.WARNING,
                context=context,
                recovery_suggestions=["Try alternative PDF library", "Check font availability", "Use simplified formatting"]
            )
        
        # Field Mapping errors
        elif any(keyword in error_str for keyword in ["mapping", "field", "coordinate"]):
            return FormPopulationError(
                message=f"Field mapping error: {str(error)}",
                category=ErrorCategory.FIELD_MAPPING,
                severity=ErrorSeverity.WARNING,
                context=context,
                recovery_suggestions=["Check field mapping configuration", "Use default mappings", "Skip problematic fields"]
            )
        
        # Validation errors
        elif any(keyword in error_str for keyword in ["validation", "required", "invalid"]):
            return FormPopulationError(
                message=f"Validation error: {str(error)}",
                category=ErrorCategory.VALIDATION,
                severity=ErrorSeverity.WARNING,
                context=context,
                recovery_suggestions=["Review data quality", "Use relaxed validation", "Generate with warnings"]
            )
        
        # System errors (default)
        else:
            return FormPopulationError(
                message=f"System error: {str(error)}",
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.CRITICAL,
                context=context,
                recovery_suggestions=["Check system resources", "Retry operation", "Contact administrator"]
            )
    
    def _log_error(self, error: FormPopulationError, context: Dict[str, Any]):
        """Log error with appropriate severity level"""
        log_message = f"[{error.category.value}] {str(error)}"
        
        if error.severity == ErrorSeverity.CRITICAL:
            self.logger.error(log_message, extra={"context": context})
        elif error.severity == ErrorSeverity.WARNING:
            self.logger.warning(log_message, extra={"context": context})
        else:
            self.logger.info(log_message, extra={"context": context})
    
    def _record_error(self, error: FormPopulationError, context: Dict[str, Any]):
        """Record error in history for pattern analysis"""
        error_record = {
            "timestamp": error.timestamp.isoformat(),
            "category": error.category.value,
            "severity": error.severity.value,
            "message": str(error),
            "context": context,
            "recovery_suggestions": error.recovery_suggestions
        }
        
        self.error_history.append(error_record)
        
        # Keep only last 100 errors to prevent memory bloat
        if len(self.error_history) > 100:
            self.error_history = self.error_history[-100:]
    
    def _attempt_recovery(self, error: FormPopulationError, context: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt automatic recovery based on error category"""
        
        recovery_result = {
            "attempted": False,
            "successful": False,
            "method": None,
            "user_action_required": False
        }
        
        # Only attempt recovery for non-critical errors
        if error.severity == ErrorSeverity.CRITICAL:
            recovery_result["user_action_required"] = True
            return recovery_result
        
        recovery_result["attempted"] = True
        
        # Try category-specific recovery strategies
        if error.category == ErrorCategory.CRM_DATA:
            recovery_result.update(self._recover_crm_data_error(error, context))
        elif error.category == ErrorCategory.FORM_TEMPLATE:
            recovery_result.update(self._recover_template_error(error, context))
        elif error.category == ErrorCategory.FIELD_MAPPING:
            recovery_result.update(self._recover_mapping_error(error, context))
        elif error.category == ErrorCategory.PDF_GENERATION:
            recovery_result.update(self._recover_pdf_error(error, context))
        elif error.category == ErrorCategory.VALIDATION:
            recovery_result.update(self._recover_validation_error(error, context))
        
        return recovery_result
    
    def _recover_crm_data_error(self, error: FormPopulationError, context: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt recovery for CRM data errors"""
        try:
            # Use placeholder values for missing non-critical fields
            transaction_id = context.get("transaction_id", "unknown")
            form_type = context.get("form_type", "unknown")
            
            placeholder_data = {
                "transaction_id": transaction_id,
                "form_type": form_type,
                "fields": {
                    "buyer_name": "[BUYER NAME REQUIRED]",
                    "seller_name": "[SELLER NAME REQUIRED]", 
                    "property_address": "[PROPERTY ADDRESS REQUIRED]",
                    "purchase_price": "[PURCHASE PRICE REQUIRED]",
                    "closing_date": "[CLOSING DATE REQUIRED]",
                    "contract_date": datetime.now().strftime("%m/%d/%Y")
                },
                "data_quality": "placeholder_fallback",
                "requires_manual_completion": True
            }
            
            # Store placeholder data in context for caller to use
            context["fallback_data"] = placeholder_data
            
            return {
                "successful": True,
                "method": "placeholder_fallback",
                "user_action_required": True,
                "message": "Generated form with placeholder data requiring manual completion"
            }
            
        except Exception as recovery_error:
            return {
                "successful": False,
                "method": "placeholder_fallback",
                "error": str(recovery_error)
            }
    
    def _recover_template_error(self, error: FormPopulationError, context: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt recovery for template errors"""
        try:
            # Use generic template coordinates
            generic_template = {
                "form_name": "generic_template",
                "pages": 1,
                "field_mappings": {
                    "buyer_name": {"page": 1, "coordinates": {"x": 100, "y": 700, "width": 200, "height": 20}},
                    "seller_name": {"page": 1, "coordinates": {"x": 100, "y": 650, "width": 200, "height": 20}},
                    "property_address": {"page": 1, "coordinates": {"x": 100, "y": 600, "width": 300, "height": 20}},
                    "purchase_price": {"page": 1, "coordinates": {"x": 100, "y": 550, "width": 150, "height": 20}},
                    "closing_date": {"page": 1, "coordinates": {"x": 100, "y": 500, "width": 150, "height": 20}}
                }
            }
            
            context["fallback_template"] = generic_template
            
            return {
                "successful": True,
                "method": "generic_template",
                "user_action_required": False,
                "message": "Using generic template coordinates"
            }
            
        except Exception as recovery_error:
            return {
                "successful": False,
                "method": "generic_template",
                "error": str(recovery_error)
            }
    
    def _recover_mapping_error(self, error: FormPopulationError, context: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt recovery for field mapping errors"""
        try:
            # Use fuzzy field matching
            form_data = context.get("form_data", {})
            if "fields" in form_data:
                # Apply default mappings for common fields
                default_mappings = {
                    "buyer": "buyer_name",
                    "seller": "seller_name", 
                    "address": "property_address",
                    "price": "purchase_price",
                    "date": "contract_date"
                }
                
                # Update context with corrected mappings
                context["corrected_mappings"] = default_mappings
                
                return {
                    "successful": True,
                    "method": "fuzzy_mapping",
                    "user_action_required": False,
                    "message": "Applied fuzzy field matching"
                }
            
            return {
                "successful": False,
                "method": "fuzzy_mapping",
                "error": "No form data available for mapping correction"
            }
            
        except Exception as recovery_error:
            return {
                "successful": False,
                "method": "fuzzy_mapping", 
                "error": str(recovery_error)
            }
    
    def _recover_pdf_error(self, error: FormPopulationError, context: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt recovery for PDF generation errors"""
        try:
            # Suggest HTML generation as fallback
            context["use_html_fallback"] = True
            
            return {
                "successful": True,
                "method": "html_fallback",
                "user_action_required": False,
                "message": "Switching to HTML form generation"
            }
            
        except Exception as recovery_error:
            return {
                "successful": False,
                "method": "html_fallback",
                "error": str(recovery_error)
            }
    
    def _recover_validation_error(self, error: FormPopulationError, context: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt recovery for validation errors"""
        try:
            # Allow form generation with validation warnings
            context["ignore_validation_warnings"] = True
            context["validation_bypassed"] = True
            
            return {
                "successful": True,
                "method": "validation_bypass",
                "user_action_required": True,
                "message": "Generated form with validation warnings - requires manual review"
            }
            
        except Exception as recovery_error:
            return {
                "successful": False,
                "method": "validation_bypass",
                "error": str(recovery_error)
            }
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of recent errors for debugging"""
        if not self.error_history:
            return {"total_errors": 0, "categories": {}, "recent_errors": []}
        
        # Count by category
        category_counts = {}
        for error in self.error_history:
            category = error["category"]
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Get recent errors (last 10)
        recent_errors = self.error_history[-10:]
        
        return {
            "total_errors": len(self.error_history),
            "categories": category_counts,
            "recent_errors": recent_errors,
            "generated_at": datetime.now().isoformat()
        }
    
    def safe_execute(self, operation_func, context: Dict[str, Any], *args, **kwargs) -> Dict[str, Any]:
        """Execute an operation with comprehensive error handling"""
        try:
            result = operation_func(*args, **kwargs)
            return {
                "success": True,
                "result": result,
                "errors": None
            }
            
        except Exception as e:
            error_handling_result = self.handle_error(e, context)
            
            return {
                "success": False,
                "result": None,
                "errors": error_handling_result,
                "context": context
            }

def main():
    """Test the error handling framework"""
    print("🚀 Error Handling Framework - ENGINE003")
    print("=" * 50)
    
    error_handler = ErrorHandlingFramework()
    
    # Test different error scenarios
    test_scenarios = [
        {
            "name": "CRM Data Error",
            "error": Exception("no such table: transactions"),
            "context": {"transaction_id": "test_001", "operation": "crm_data_fetch"}
        },
        {
            "name": "Template Error", 
            "error": FileNotFoundError("template.json not found"),
            "context": {"form_type": "purchase_agreement", "operation": "template_load"}
        },
        {
            "name": "Validation Error",
            "error": ValueError("required field 'buyer_name' is missing"),
            "context": {"form_data": {"fields": {}}, "operation": "validation"}
        }
    ]
    
    print("\n🧪 Testing Error Handling Scenarios:")
    for scenario in test_scenarios:
        print(f"\n📋 Testing: {scenario['name']}")
        result = error_handler.handle_error(scenario["error"], scenario["context"])
        
        print(f"   ✅ Handled: {result['error_handled']}")
        print(f"   📁 Category: {result['error_category']}")
        print(f"   ⚠️  Severity: {result['error_severity']}")
        print(f"   🔄 Recovery: {result['recovery_successful']}")
        if result["recovery_successful"]:
            print(f"   🛠️  Method: {result['recovery_method']}")
    
    # Show error summary
    print(f"\n📊 Error Summary:")
    summary = error_handler.get_error_summary()
    print(f"   Total Errors: {summary['total_errors']}")
    print(f"   Categories: {summary['categories']}")
    
    print(f"\n✅ ENGINE003 Complete: Comprehensive Error Handling Framework")
    print(f"🔄 Ready for integration with Form Population Engine")

if __name__ == "__main__":
    main()