"""
Security Management Module
Consolidated security testing and hardening
"""

import json
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from .config import get_config
from .logger import setup_logger


class SecurityManager:
    """Unified security testing and hardening manager"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = setup_logger("security")
        self.base_url = self.config.production_url
        
    def analyze_penetration_test_results(self, test_file: Optional[str] = None) -> Dict[str, Any]:
        """Analyze existing penetration test results"""
        self.logger.security("Analyzing penetration test results...")
        
        if test_file is None:
            test_file = "penetration_test_report.json"
        
        try:
            test_path = Path(test_file)
            if not test_path.exists():
                self.logger.warning(f"Penetration test file not found: {test_file}")
                return self._run_basic_security_tests()
            
            with open(test_path, 'r') as f:
                pen_test = json.load(f)
            
            # Analyze results
            vulnerabilities = {
                'critical': [],
                'high': [],
                'medium': [],
                'low': []
            }
            
            passed_tests = 0
            failed_tests = 0
            
            for result in pen_test['results']:
                if result['status'] == 'FAIL':
                    failed_tests += 1
                    severity = result['severity'].lower()
                    if severity in vulnerabilities:
                        vulnerabilities[severity].append({
                            'test': result['test_name'],
                            'description': result['description']
                        })
                elif result['status'] == 'PASS':
                    passed_tests += 1
            
            analysis = {
                'total_tests': pen_test['total_tests'],
                'passed': passed_tests,
                'failed': failed_tests,
                'vulnerabilities': vulnerabilities,
                'security_score': round((passed_tests / pen_test['total_tests']) * 100, 1)
            }
            
            self.logger.info(f"Security Score: {analysis['security_score']}% ({passed_tests}/{pen_test['total_tests']} tests passed)")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to analyze penetration test results: {e}")
            return self._run_basic_security_tests()
    
    def _run_basic_security_tests(self) -> Dict[str, Any]:
        """Run basic security tests if penetration test results unavailable"""
        self.logger.security("Running basic security tests...")
        
        tests = {
            'ssl_certificate': self._test_ssl_certificate(),
            'security_headers': self._test_security_headers(),
            'http_methods': self._test_http_methods(),
            'error_handling': self._test_error_handling()
        }
        
        passed = sum(1 for result in tests.values() if result.get('passed', False))
        total = len(tests)
        
        return {
            'total_tests': total,
            'passed': passed,
            'failed': total - passed,
            'security_score': round((passed / total) * 100, 1),
            'test_results': tests
        }
    
    def _test_ssl_certificate(self) -> Dict[str, Any]:
        """Test SSL certificate configuration"""
        try:
            response = requests.get(self.base_url, timeout=10)
            ssl_active = response.url.startswith('https://')
            
            return {
                'passed': ssl_active,
                'details': {
                    'https_redirect': ssl_active,
                    'final_url': response.url
                }
            }
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    def _test_security_headers(self) -> Dict[str, Any]:
        """Test security headers"""
        try:
            response = requests.get(self.base_url, timeout=10)
            headers = response.headers
            
            required_headers = {
                'Strict-Transport-Security': 'HSTS',
                'X-Content-Type-Options': 'MIME sniffing protection',
                'X-Frame-Options': 'Clickjacking protection',
                'X-XSS-Protection': 'XSS protection'
            }
            
            present_headers = {}
            for header, description in required_headers.items():
                present_headers[header] = header in headers
            
            passed = sum(present_headers.values()) >= 3  # At least 3 out of 4
            
            return {
                'passed': passed,
                'details': present_headers,
                'score': f"{sum(present_headers.values())}/{len(required_headers)}"
            }
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    def _test_http_methods(self) -> Dict[str, Any]:
        """Test HTTP method restrictions"""
        try:
            # Test dangerous methods
            dangerous_methods = ['TRACE', 'PUT', 'DELETE', 'PATCH']
            blocked_methods = 0
            
            for method in dangerous_methods:
                response = requests.request(method, self.base_url, timeout=5)
                if response.status_code in [405, 501]:  # Method not allowed
                    blocked_methods += 1
            
            passed = blocked_methods >= len(dangerous_methods) - 1  # Allow some flexibility
            
            return {
                'passed': passed,
                'details': {
                    'blocked_methods': blocked_methods,
                    'total_tested': len(dangerous_methods)
                }
            }
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    def _test_error_handling(self) -> Dict[str, Any]:
        """Test error handling security"""
        try:
            # Test 404 handling
            response = requests.get(f"{self.base_url}/nonexistent-page", timeout=5)
            
            # Should return 404, not 500 or expose debug info
            secure_404 = response.status_code == 404
            no_debug_info = 'debug' not in response.text.lower()
            
            passed = secure_404 and no_debug_info
            
            return {
                'passed': passed,
                'details': {
                    'status_code': response.status_code,
                    'debug_info_exposed': not no_debug_info
                }
            }
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    def generate_security_fixes(self) -> Dict[str, str]:
        """Generate security fix implementations"""
        self.logger.security("Generating security fixes...")
        
        fixes = {
            'rate_limiting': self._generate_rate_limiting_code(),
            'security_headers': self._generate_security_headers_code(),
            'input_validation': self._generate_input_validation_code(),
            'error_handling': self._generate_error_handling_code(),
            'session_security': self._generate_session_security_code()
        }
        
        return fixes
    
    def _generate_rate_limiting_code(self) -> str:
        """Generate rate limiting implementation"""
        return '''
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Apply to sensitive endpoints
@app.route('/api/chat', methods=['POST'])
@limiter.limit("5 per minute")
def chat_endpoint():
    # Existing implementation
    pass

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    # Existing implementation
    pass
'''
    
    def _generate_security_headers_code(self) -> str:
        """Generate security headers implementation"""
        return f'''
@app.after_request
def add_security_headers(response):
    """Add comprehensive security headers"""
    # Content Security Policy
    csp_policy = (
        "default-src {' '.join(self.config.security.csp_default_src)}; "
        "script-src {' '.join(self.config.security.csp_script_src)}; "
        "style-src {' '.join(self.config.security.csp_style_src)}; "
        "img-src {' '.join(self.config.security.csp_img_src)}; "
        "connect-src 'self'"
    )
    response.headers['Content-Security-Policy'] = csp_policy
    
    # Security headers
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    
    # Remove server header
    response.headers.pop('Server', None)
    
    return response
'''
    
    def _generate_input_validation_code(self) -> str:
        """Generate input validation implementation"""
        return '''
import bleach
import re
from flask import request, jsonify

def sanitize_input(text):
    """Sanitize user input to prevent XSS"""
    if not text:
        return text
    # Remove HTML tags
    cleaned = bleach.clean(text, tags=[], strip=True)
    # Basic SQL injection prevention
    cleaned = re.sub(r'[;\\'"\\-\\-\\/\\*]', '', cleaned)
    return cleaned

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Example usage in routes
@app.route('/api/clients', methods=['POST'])
def create_client():
    data = request.get_json()
    
    # Validate inputs
    if 'email' in data and not validate_email(data['email']):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Sanitize inputs
    for field in ['name', 'description', 'notes']:
        if field in data:
            data[field] = sanitize_input(data[field])
    
    # Continue with processing
'''
    
    def _generate_error_handling_code(self) -> str:
        """Generate secure error handling implementation"""
        return '''
@app.errorhandler(404)
def not_found_error(error):
    """Secure 404 handler"""
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Secure 500 handler"""
    # Log actual error for debugging
    app.logger.error(f'Internal error: {error}')
    # Return generic message to client
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """Global exception handler"""
    app.logger.error(f'Unhandled exception: {e}')
    return jsonify({'error': 'An error occurred'}), 500

# Disable debug in production
if app.config.get('ENV') == 'production':
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
'''
    
    def _generate_session_security_code(self) -> str:
        """Generate session security implementation"""
        return f'''
# Session security configuration
app.config['SESSION_COOKIE_SECURE'] = {self.config.security.session_cookie_secure}
app.config['SESSION_COOKIE_HTTPONLY'] = {self.config.security.session_cookie_httponly}
app.config['SESSION_COOKIE_SAMESITE'] = '{self.config.security.session_cookie_samesite}'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# CSRF protection
app.config['WTF_CSRF_ENABLED'] = {self.config.security.csrf_enabled}
app.config['WTF_CSRF_TIME_LIMIT'] = None
'''
    
    def create_supabase_rls_policies(self) -> str:
        """Generate Supabase Row Level Security policies"""
        return '''
-- Enable RLS on all tables
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

-- Client access policies
CREATE POLICY "Users can view own clients" ON clients
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own clients" ON clients
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own clients" ON clients
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own clients" ON clients
    FOR DELETE USING (auth.uid() = user_id);

-- Property access policies (read-only for all authenticated users)
CREATE POLICY "Users can view all properties" ON properties
    FOR SELECT USING (auth.role() = 'authenticated');

-- Transaction access policies
CREATE POLICY "Users can manage own transactions" ON transactions
    FOR ALL USING (auth.uid() = agent_id);
'''
    
    def comprehensive_security_audit(self) -> Dict[str, Any]:
        """Run comprehensive security audit"""
        self.logger.section("COMPREHENSIVE SECURITY AUDIT", level=1)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'penetration_test_analysis': None,
            'security_fixes': None,
            'supabase_rls': None,
            'recommendations': []
        }
        
        # 1. Analyze penetration test results
        self.logger.info("Step 1: Analyzing Penetration Test Results")
        results['penetration_test_analysis'] = self.analyze_penetration_test_results()
        
        # 2. Generate security fixes
        self.logger.info("Step 2: Generating Security Fixes")
        results['security_fixes'] = self.generate_security_fixes()
        
        # 3. Create Supabase RLS policies
        self.logger.info("Step 3: Creating Supabase RLS Policies")
        results['supabase_rls'] = self.create_supabase_rls_policies()
        
        # 4. Generate recommendations
        self.logger.info("Step 4: Generating Security Recommendations")
        results['recommendations'] = self._generate_security_recommendations(
            results['penetration_test_analysis']
        )
        
        # Summary
        self.logger.section("SECURITY AUDIT SUMMARY", level=2)
        security_score = results['penetration_test_analysis'].get('security_score', 0)
        fixes_count = len(results['security_fixes'])
        recommendations_count = len(results['recommendations'])
        
        self.logger.info(f"Security Score: {security_score}%")
        self.logger.info(f"Security Fixes Generated: {fixes_count}")
        self.logger.info(f"Recommendations: {recommendations_count}")
        
        if security_score >= 90:
            self.logger.success("Security posture: EXCELLENT")
        elif security_score >= 80:
            self.logger.success("Security posture: GOOD")
        elif security_score >= 70:
            self.logger.warning("Security posture: ACCEPTABLE")
        else:
            self.logger.error("Security posture: NEEDS IMPROVEMENT")
        
        return results
    
    def _generate_security_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate security recommendations based on analysis"""
        recommendations = []
        
        security_score = analysis.get('security_score', 0)
        
        if security_score < 90:
            recommendations.extend([
                "1. IMMEDIATE ACTIONS:",
                "   - Apply all generated security fixes",
                "   - Update requirements.txt with security dependencies",
                "   - Configure Supabase RLS policies",
                ""
            ])
        
        recommendations.extend([
            "2. APPLICATION SECURITY:",
            "   - Implement rate limiting on all API endpoints",
            "   - Add Content Security Policy headers",
            "   - Sanitize all user inputs",
            "   - Use secure session configuration",
            "",
            "3. INFRASTRUCTURE SECURITY:",
            "   - Enable Web Application Firewall (WAF)",
            "   - Configure IP allowlisting for admin functions",
            "   - Implement API key authentication",
            "   - Set up security monitoring and alerting",
            "",
            "4. DATA SECURITY:",
            "   - Implement database encryption at rest",
            "   - Configure Row Level Security policies",
            "   - Regular security audits and penetration testing",
            "   - Backup encryption and access controls",
            "",
            "5. OPERATIONAL SECURITY:",
            "   - Regular security dependency updates",
            "   - Implement secrets rotation",
            "   - Security incident response plan",
            "   - Employee security training"
        ])
        
        return recommendations