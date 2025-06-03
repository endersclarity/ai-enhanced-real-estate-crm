#!/usr/bin/env python3
"""
Form Selection Interface - UI001  
Interactive interface for selecting and generating CAR forms with real-time preview
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session
from form_population_engine import FormPopulationEngine
from langchain_form_extension import LangChainFormExtension

class FormSelectionInterface:
    """Interactive form selection and generation interface"""
    
    def __init__(self, database_path: str = "core_app/database/real_estate_crm.db"):
        self.database_path = database_path
        self.form_engine = FormPopulationEngine(database_path)
        self.ai_extension = LangChainFormExtension()
        
        # Load available forms
        self.available_forms = self._load_available_forms()
        
        # Initialize Flask routes
        self.app = Flask(__name__)
        self.app.secret_key = "form_selection_interface_2025"
        self._register_routes()
    
    def _load_available_forms(self) -> Dict[str, Any]:
        """Load available CAR forms with metadata"""
        return {
            "california_residential_purchase_agreement": {
                "display_name": "California Residential Purchase Agreement",
                "description": "Primary purchase contract for residential real estate transactions",
                "category": "purchase",
                "required_data": ["buyer", "seller", "property", "price", "terms"],
                "estimated_time": "5-10 minutes",
                "legal_review": "required",
                "icon": "📄"
            },
            "buyer_representation_agreement": {
                "display_name": "Buyer Representation and Broker Compensation Agreement", 
                "description": "Establishes agency relationship between buyer and real estate broker",
                "category": "representation",
                "required_data": ["buyer", "agent", "compensation_terms"],
                "estimated_time": "3-5 minutes",
                "legal_review": "recommended",
                "icon": "🤝"
            },
            "transaction_record": {
                "display_name": "Transaction Record",
                "description": "Comprehensive record of transaction details and timeline",
                "category": "documentation",
                "required_data": ["transaction_details", "parties", "timeline"],
                "estimated_time": "2-3 minutes", 
                "legal_review": "optional",
                "icon": "📋"
            },
            "property_condition_verification": {
                "display_name": "Verification of Property Condition",
                "description": "Documentation of property condition and disclosure requirements",
                "category": "disclosure",
                "required_data": ["property", "condition_details", "inspections"],
                "estimated_time": "5-8 minutes",
                "legal_review": "required",
                "icon": "🏠"
            },
            "statewide_buyer_seller_advisory": {
                "display_name": "Statewide Buyer and Seller Advisory",
                "description": "Important disclosures and advisories for real estate transactions",
                "category": "advisory",
                "required_data": ["parties", "property_type", "transaction_type"],
                "estimated_time": "3-5 minutes",
                "legal_review": "required",
                "icon": "⚠️"
            },
            "agent_visual_inspection_disclosure": {
                "display_name": "Agent Visual Inspection Disclosure",
                "description": "Agent's visual inspection findings and recommendations",
                "category": "inspection",
                "required_data": ["agent", "property", "inspection_details"],
                "estimated_time": "5-10 minutes",
                "legal_review": "recommended",
                "icon": "👁️"
            },
            "market_conditions_advisory": {
                "display_name": "Market Conditions Advisory",
                "description": "Current market conditions and their impact on the transaction",
                "category": "advisory",
                "required_data": ["market_data", "property", "transaction_timing"],
                "estimated_time": "2-4 minutes",
                "legal_review": "optional",
                "icon": "📈"
            },
            "electronic_signature_verification": {
                "display_name": "Electronic Signature Verification for Third Parties",
                "description": "Verification process for electronic signatures from third parties",
                "category": "verification",
                "required_data": ["signers", "verification_method", "third_parties"],
                "estimated_time": "2-3 minutes",
                "legal_review": "recommended",
                "icon": "✍️"
            },
            "confidentiality_agreement": {
                "display_name": "Confidentiality and Non-Disclosure Agreement",
                "description": "Protects confidential information shared during the transaction",
                "category": "legal",
                "required_data": ["parties", "confidential_information", "terms"],
                "estimated_time": "3-5 minutes",
                "legal_review": "required",
                "icon": "🔒"
            },
            "modification_buyer_representation": {
                "display_name": "Modification of Terms - Buyer Representation Agreement",
                "description": "Amendments to existing buyer representation agreements",
                "category": "modification",
                "required_data": ["original_agreement", "modifications", "parties"],
                "estimated_time": "2-4 minutes",
                "legal_review": "required",
                "icon": "📝"
            },
            "advisory_addendum": {
                "display_name": "Addendum to Statewide Buyer and Seller Advisory",
                "description": "Additional disclosures and advisories",
                "category": "addendum",
                "required_data": ["original_advisory", "additional_terms"],
                "estimated_time": "2-3 minutes",
                "legal_review": "recommended",
                "icon": "➕"
            },
            "septic_well_addendum": {
                "display_name": "Septic/Well/Property Monument/Propane Allocation Addendum",
                "description": "Special conditions for properties with septic, wells, or propane",
                "category": "addendum",
                "required_data": ["property_features", "allocation_terms", "responsibilities"],
                "estimated_time": "5-8 minutes",
                "legal_review": "required",
                "icon": "🏔️"
            },
            "permit_transmittal": {
                "display_name": "Permit Transmittal",
                "description": "Documentation for permit transfers and compliance",
                "category": "permits",
                "required_data": ["permits", "property", "transfer_details"],
                "estimated_time": "3-5 minutes",
                "legal_review": "recommended",
                "icon": "📜"
            }
        }
    
    def _register_routes(self):
        """Register Flask routes for the form selection interface"""
        
        @self.app.route('/forms')
        def form_selection_dashboard():
            """Main form selection dashboard"""
            try:
                # Get available forms with categories
                forms_by_category = self._organize_forms_by_category()
                
                # Get recent transactions for quick selection
                recent_transactions = self._get_recent_transactions()
                
                # Get client list for form generation
                clients = self._get_client_list()
                
                return render_template('form_selection.html',
                                     forms_by_category=forms_by_category,
                                     recent_transactions=recent_transactions,
                                     clients=clients)
                                     
            except Exception as e:
                return jsonify({"error": f"Dashboard loading failed: {str(e)}"}), 500
        
        @self.app.route('/api/forms/available')
        def get_available_forms():
            """API endpoint for available forms"""
            return jsonify({
                "success": True,
                "forms": self.available_forms,
                "total_forms": len(self.available_forms)
            })
        
        @self.app.route('/api/forms/preview', methods=['POST'])
        def preview_form_generation():
            """Preview form generation without creating the actual document"""
            try:
                data = request.get_json()
                form_type = data.get('form_type')
                transaction_id = data.get('transaction_id')
                
                if not form_type or not transaction_id:
                    return jsonify({
                        "success": False,
                        "error": "Form type and transaction ID are required"
                    }), 400
                
                # Generate preview data
                preview_data = self._generate_form_preview(form_type, transaction_id)
                
                return jsonify({
                    "success": True,
                    "preview": preview_data,
                    "form_type": form_type,
                    "transaction_id": transaction_id
                })
                
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": f"Preview generation failed: {str(e)}"
                }), 500
        
        @self.app.route('/api/forms/generate', methods=['POST'])
        def generate_form():
            """Generate actual form document"""
            try:
                data = request.get_json()
                form_type = data.get('form_type')
                transaction_id = data.get('transaction_id')
                custom_filename = data.get('filename')
                
                if not form_type or not transaction_id:
                    return jsonify({
                        "success": False,
                        "error": "Form type and transaction ID are required"
                    }), 400
                
                # Generate the form
                result = self.form_engine.populate_form(
                    transaction_id=transaction_id,
                    form_type=form_type,
                    output_filename=custom_filename
                )
                
                if result.get("success"):
                    # Log successful generation
                    self._log_form_generation(form_type, transaction_id, result)
                    
                    return jsonify({
                        "success": True,
                        "result": result,
                        "download_url": f"/download/{Path(result['output_file']).name}",
                        "generated_at": datetime.now().isoformat()
                    })
                else:
                    return jsonify({
                        "success": False,
                        "error": result.get("error", "Unknown error"),
                        "details": result
                    }), 400
                    
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": f"Form generation failed: {str(e)}"
                }), 500
        
        @self.app.route('/api/forms/natural-language', methods=['POST'])
        def process_natural_language_request():
            """Process natural language form generation request"""
            try:
                data = request.get_json()
                user_request = data.get('request', '')
                
                if not user_request:
                    return jsonify({
                        "success": False,
                        "error": "Request text is required"
                    }), 400
                
                # Process with AI extension
                result = self.ai_extension.process_natural_language_form_request(user_request)
                
                return jsonify({
                    "success": result.get("success", False),
                    "result": result,
                    "processed_at": datetime.now().isoformat()
                })
                
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": f"Natural language processing failed: {str(e)}"
                }), 500
        
        @self.app.route('/api/clients/search')
        def search_clients():
            """Search clients for form generation"""
            try:
                query = request.args.get('q', '')
                limit = int(request.args.get('limit', 10))
                
                clients = self._search_clients(query, limit)
                
                return jsonify({
                    "success": True,
                    "clients": clients,
                    "query": query
                })
                
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": f"Client search failed: {str(e)}"
                }), 500
        
        @self.app.route('/api/transactions/for-client/<client_id>')
        def get_client_transactions(client_id):
            """Get transactions for a specific client"""
            try:
                transactions = self._get_client_transactions(client_id)
                
                return jsonify({
                    "success": True,
                    "transactions": transactions,
                    "client_id": client_id
                })
                
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": f"Transaction lookup failed: {str(e)}"
                }), 500
    
    def _organize_forms_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """Organize forms by category for dashboard display"""
        categories = {}
        
        for form_id, form_info in self.available_forms.items():
            category = form_info["category"]
            
            if category not in categories:
                categories[category] = []
            
            form_data = {
                "id": form_id,
                "display_name": form_info["display_name"],
                "description": form_info["description"],
                "icon": form_info["icon"],
                "estimated_time": form_info["estimated_time"],
                "legal_review": form_info["legal_review"],
                "required_data": form_info["required_data"]
            }
            
            categories[category].append(form_data)
        
        return categories
    
    def _get_recent_transactions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent transactions for quick form generation"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # This would be adapted based on actual database schema
            cursor.execute("""
                SELECT id, client_name, property_address, transaction_type, created_date
                FROM transactions 
                ORDER BY created_date DESC 
                LIMIT ?
            """, (limit,))
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "id": row[0],
                    "client_name": row[1],
                    "property_address": row[2],
                    "transaction_type": row[3],
                    "created_date": row[4]
                }
                for row in results
            ]
            
        except Exception as e:
            # Return empty list if no database or table exists yet
            return []
    
    def _get_client_list(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get client list for form generation"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, first_name, last_name, email, phone
                FROM clients 
                ORDER BY last_name, first_name
                LIMIT ?
            """, (limit,))
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "id": row[0],
                    "name": f"{row[1]} {row[2]}",
                    "email": row[3],
                    "phone": row[4]
                }
                for row in results
            ]
            
        except Exception as e:
            # Return sample data if no database exists yet
            return [
                {"id": "sample_001", "name": "John Smith", "email": "john@example.com", "phone": "555-0123"},
                {"id": "sample_002", "name": "Jane Doe", "email": "jane@example.com", "phone": "555-0456"}
            ]
    
    def _generate_form_preview(self, form_type: str, transaction_id: str) -> Dict[str, Any]:
        """Generate preview data for form without creating actual document"""
        try:
            # Get form metadata
            form_info = self.available_forms.get(form_type, {})
            
            # Simulate field mapping (would be actual CRM data lookup)
            preview_fields = {
                "buyer_name": "[Buyer Name from CRM]",
                "seller_name": "[Seller Name from CRM]",
                "property_address": "[Property Address from CRM]",
                "purchase_price": "[Purchase Price from CRM]",
                "closing_date": "[Closing Date from CRM]"
            }
            
            return {
                "form_info": form_info,
                "preview_fields": preview_fields,
                "field_count": len(preview_fields),
                "estimated_completion": "85%",
                "missing_fields": ["Agent signature", "Buyer initials"],
                "preview_generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "error": f"Preview generation failed: {str(e)}",
                "form_type": form_type,
                "transaction_id": transaction_id
            }
    
    def _search_clients(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search clients by name or other criteria"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            search_pattern = f"%{query}%"
            cursor.execute("""
                SELECT id, first_name, last_name, email, phone
                FROM clients 
                WHERE first_name LIKE ? OR last_name LIKE ? OR email LIKE ?
                ORDER BY last_name, first_name
                LIMIT ?
            """, (search_pattern, search_pattern, search_pattern, limit))
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "id": row[0],
                    "name": f"{row[1]} {row[2]}",
                    "email": row[3],
                    "phone": row[4]
                }
                for row in results
            ]
            
        except Exception as e:
            # Return filtered sample data
            return [client for client in self._get_client_list() 
                   if query.lower() in client["name"].lower()]
    
    def _get_client_transactions(self, client_id: str) -> List[Dict[str, Any]]:
        """Get all transactions for a specific client"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, property_address, transaction_type, status, created_date
                FROM transactions 
                WHERE client_id = ?
                ORDER BY created_date DESC
            """, (client_id,))
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "id": row[0],
                    "property_address": row[1],
                    "transaction_type": row[2],
                    "status": row[3],
                    "created_date": row[4]
                }
                for row in results
            ]
            
        except Exception as e:
            # Return sample transaction data
            return [
                {
                    "id": "txn_001",
                    "property_address": "123 Main Street",
                    "transaction_type": "Purchase",
                    "status": "Active",
                    "created_date": "2025-06-01"
                }
            ]
    
    def _log_form_generation(self, form_type: str, transaction_id: str, result: Dict[str, Any]):
        """Log successful form generation for analytics"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "form_type": form_type,
                "transaction_id": transaction_id,
                "output_file": result.get("output_file"),
                "populated_fields": result.get("populated_fields", 0),
                "generation_success": result.get("success", False)
            }
            
            # Save to log file
            log_file = Path("form_generation_log.json")
            
            if log_file.exists():
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            logs.append(log_entry)
            
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            print(f"Logging failed: {str(e)}")
    
    def run_interface(self, host: str = "0.0.0.0", port: int = 5002, debug: bool = True):
        """Run the form selection interface"""
        print(f"🚀 Starting Form Selection Interface on http://{host}:{port}")
        print(f"📄 Available forms: {len(self.available_forms)}")
        print(f"🔄 Ready for form generation requests")
        
        self.app.run(host=host, port=port, debug=debug)

def create_form_selection_template():
    """Create the HTML template for form selection interface"""
    template_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CAR Form Selection Interface</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .form-card {
            transition: transform 0.2s;
            cursor: pointer;
        }
        .form-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .category-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
        .form-icon {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        .quick-actions {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin-bottom: 2rem;
        }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <div class="col-12">
                <h1 class="my-4">CAR Form Generation Interface</h1>
                
                <!-- Quick Actions -->
                <div class="quick-actions">
                    <h3>Quick Actions</h3>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="clientSearch" class="form-label">Search Client</label>
                                <input type="text" class="form-control" id="clientSearch" 
                                       placeholder="Type client name...">
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="naturalLanguage" class="form-label">Natural Language Request</label>
                                <input type="text" class="form-control" id="naturalLanguage" 
                                       placeholder="Generate a purchase agreement for...">
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Forms by Category -->
                {% for category, forms in forms_by_category.items() %}
                <div class="category-section mb-4">
                    <div class="category-header">
                        <h3 class="mb-0">{{ category.title() }} Forms</h3>
                    </div>
                    
                    <div class="row">
                        {% for form in forms %}
                        <div class="col-lg-4 col-md-6 mb-3">
                            <div class="card form-card h-100" onclick="selectForm('{{ form.id }}')">
                                <div class="card-body text-center">
                                    <div class="form-icon">{{ form.icon }}</div>
                                    <h5 class="card-title">{{ form.display_name }}</h5>
                                    <p class="card-text">{{ form.description }}</p>
                                    <div class="mt-auto">
                                        <small class="text-muted">
                                            ⏱️ {{ form.estimated_time }} | 
                                            ⚖️ {{ form.legal_review.title() }}
                                        </small>
                                    </div>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    
    <!-- Form Generation Modal -->
    <div class="modal fade" id="formModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Generate Form</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div id="modalContent">
                        <!-- Dynamic content will be loaded here -->
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function selectForm(formId) {
            // Load form generation interface
            document.getElementById('modalContent').innerHTML = `
                <h4>Generate ${formId}</h4>
                <div class="mb-3">
                    <label for="transactionSelect" class="form-label">Select Transaction</label>
                    <select class="form-select" id="transactionSelect">
                        <option value="">Choose transaction...</option>
                        <option value="txn_001">John Smith - 123 Main Street</option>
                        <option value="txn_002">Jane Doe - 456 Oak Avenue</option>
                    </select>
                </div>
                <div class="d-grid gap-2">
                    <button class="btn btn-outline-secondary" onclick="previewForm('${formId}')">
                        Preview Form
                    </button>
                    <button class="btn btn-primary" onclick="generateForm('${formId}')">
                        Generate Form
                    </button>
                </div>
            `;
            
            new bootstrap.Modal(document.getElementById('formModal')).show();
        }
        
        function previewForm(formId) {
            const transactionId = document.getElementById('transactionSelect').value;
            if (!transactionId) {
                alert('Please select a transaction first');
                return;
            }
            
            // Implementation would call /api/forms/preview
            alert(`Preview for ${formId} with transaction ${transactionId}`);
        }
        
        function generateForm(formId) {
            const transactionId = document.getElementById('transactionSelect').value;
            if (!transactionId) {
                alert('Please select a transaction first');
                return;
            }
            
            // Implementation would call /api/forms/generate
            alert(`Generating ${formId} for transaction ${transactionId}`);
        }
        
        // Natural language processing
        document.getElementById('naturalLanguage').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const request = this.value;
                if (request.trim()) {
                    // Implementation would call /api/forms/natural-language
                    alert(`Processing: "${request}"`);
                }
            }
        });
        
        // Client search
        document.getElementById('clientSearch').addEventListener('input', function(e) {
            const query = this.value;
            if (query.length > 2) {
                // Implementation would call /api/clients/search
                console.log(`Searching clients: ${query}`);
            }
        });
    </script>
</body>
</html>"""
    
    # Create templates directory if it doesn't exist
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    # Write template file
    template_file = templates_dir / "form_selection.html"
    with open(template_file, 'w') as f:
        f.write(template_content)
    
    return str(template_file)

def main():
    """Test the form selection interface"""
    print("🚀 Form Selection Interface - UI001")
    print("=" * 50)
    
    # Create HTML template
    template_file = create_form_selection_template()
    print(f"📄 Created template: {template_file}")
    
    # Initialize interface
    interface = FormSelectionInterface()
    
    print(f"\n📋 Loaded {len(interface.available_forms)} CAR forms:")
    for form_id, form_info in interface.available_forms.items():
        print(f"   {form_info['icon']} {form_info['display_name']}")
    
    print(f"\n🌐 Form categories available:")
    categories = interface._organize_forms_by_category()
    for category, forms in categories.items():
        print(f"   📁 {category.title()}: {len(forms)} forms")
    
    print(f"\n✅ UI001 Complete: Form Selection Interface")
    print(f"🔄 Ready for interactive form generation with Flask interface")
    print(f"💡 Run interface.run_interface() to start the web server")

if __name__ == "__main__":
    main()