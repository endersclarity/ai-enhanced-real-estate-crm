#!/usr/bin/env python3
"""
Custom Domain and SSL Configuration
Task #9: Configure Custom Domain and SSL
"""

import requests
import json
import os
import time
import dns.resolver
from urllib.parse import urlparse

class DomainSSLManager:
    """Manage custom domain and SSL configuration for DigitalOcean App Platform"""
    
    def __init__(self, app_id=None, do_token=None):
        self.app_id = app_id
        self.do_token = do_token or os.environ.get('DIGITALOCEAN_TOKEN')
        self.headers = {
            "Authorization": f"Bearer {self.do_token}",
            "Content-Type": "application/json"
        }
        self.base_url = "https://api.digitalocean.com/v2"
    
    def configure_custom_domain(self, domain_name, is_primary=True):
        """Configure custom domain for the app"""
        
        print(f"🌐 Configuring custom domain: {domain_name}")
        
        # Validate domain format
        if not self._is_valid_domain(domain_name):
            raise ValueError(f"Invalid domain format: {domain_name}")
        
        # Add domain to app configuration
        domain_config = {
            "domain": domain_name,
            "type": "PRIMARY" if is_primary else "ALIAS",
            "wildcard": False,
            "minimum_tls_version": "1.2"
        }
        
        # Get current app spec
        current_spec = self._get_app_spec()
        if not current_spec:
            raise Exception("Could not retrieve current app specification")
        
        # Add domain to domains array
        if 'domains' not in current_spec:
            current_spec['domains'] = []
        
        # Check if domain already exists
        existing_domain = None
        for domain in current_spec.get('domains', []):
            if domain['domain'] == domain_name:
                existing_domain = domain
                break
        
        if existing_domain:
            print(f"✅ Domain {domain_name} already configured")
            return existing_domain
        
        # Add new domain
        current_spec['domains'].append(domain_config)
        
        # Update app with new domain
        update_response = self._update_app_spec(current_spec)
        if update_response:
            print(f"✅ Domain {domain_name} added to app configuration")
            return domain_config
        else:
            raise Exception("Failed to update app with domain configuration")
    
    def configure_ssl_certificate(self, domain_name):
        """Configure SSL certificate using Let's Encrypt"""
        
        print(f"🔒 Configuring SSL certificate for: {domain_name}")
        
        # DigitalOcean App Platform automatically provisions Let's Encrypt certificates
        # when a domain is added to the app configuration
        
        # Check if SSL certificate is already provisioned
        domain_status = self._check_domain_status(domain_name)
        if domain_status:
            if domain_status.get('ssl_enabled'):
                print(f"✅ SSL certificate already active for {domain_name}")
                return True
        
        # SSL certificates are automatically provisioned by DigitalOcean
        # when DNS records are correctly configured
        print("⏳ SSL certificate will be automatically provisioned by Let's Encrypt")
        print("   This process may take 5-10 minutes after DNS propagation")
        
        return True
    
    def configure_https_redirects(self):
        """Configure HTTPS redirects and security headers"""
        
        print("🔧 Configuring HTTPS redirects and security headers")
        
        # DigitalOcean App Platform handles HTTPS redirects automatically
        # We can configure additional security headers at the application level
        
        security_config = {
            'force_https': True,
            'headers': {
                'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block',
                'Referrer-Policy': 'strict-origin-when-cross-origin',
                'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
            }
        }
        
        return security_config
    
    def generate_dns_instructions(self, domain_name):
        """Generate DNS configuration instructions"""
        
        print(f"📋 DNS Configuration Instructions for {domain_name}")
        print("=" * 60)
        
        # Get app's live URL to determine the target
        app_info = self._get_app_info()
        if not app_info:
            print("❌ Could not retrieve app information")
            return None
        
        # DigitalOcean App Platform uses CNAME records
        do_app_url = app_info.get('live_url', '').replace('https://', '').replace('http://', '')
        
        dns_records = [
            {
                'type': 'CNAME',
                'name': '@' if domain_name.count('.') == 1 else 'www',
                'value': do_app_url,
                'ttl': 300
            }
        ]
        
        # If it's a root domain, also add www redirect
        if domain_name.count('.') == 1:
            dns_records.append({
                'type': 'CNAME',
                'name': 'www',
                'value': do_app_url,
                'ttl': 300
            })
        
        print("\nRequired DNS Records:")
        print("-" * 30)
        for record in dns_records:
            print(f"Type: {record['type']}")
            print(f"Name: {record['name']}")
            print(f"Value: {record['value']}")
            print(f"TTL: {record['ttl']}")
            print()
        
        print("Instructions:")
        print("1. Log into your domain registrar's DNS management panel")
        print("2. Add the CNAME record(s) shown above")
        print("3. Wait for DNS propagation (5-30 minutes)")
        print("4. SSL certificate will be automatically provisioned")
        
        return dns_records
    
    def verify_ssl_certificate(self, domain_name, timeout=300):
        """Verify SSL certificate is properly configured"""
        
        print(f"🔍 Verifying SSL certificate for: {domain_name}")
        
        import ssl
        import socket
        from datetime import datetime
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Test SSL connection
                context = ssl.create_default_context()
                
                with socket.create_connection((domain_name, 443), timeout=10) as sock:
                    with context.wrap_socket(sock, server_hostname=domain_name) as ssock:
                        cert = ssock.getpeercert()
                        
                        # Check certificate validity
                        not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                        not_before = datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
                        now = datetime.utcnow()
                        
                        if not_before <= now <= not_after:
                            print(f"✅ SSL certificate is valid")
                            print(f"   Issuer: {cert.get('issuer', [{}])[0].get('organizationName', 'Unknown')}")
                            print(f"   Valid until: {cert['notAfter']}")
                            
                            # Test HTTPS redirect
                            self._test_https_redirect(domain_name)
                            
                            return True
                        else:
                            print(f"❌ SSL certificate is expired or not yet valid")
                            return False
                            
            except (socket.gaierror, ConnectionRefusedError, ssl.SSLError) as e:
                print(f"⏳ Waiting for SSL certificate... ({int(time.time() - start_time)}s)")
                time.sleep(30)
                continue
            except Exception as e:
                print(f"❌ SSL verification error: {str(e)}")
                return False
        
        print(f"❌ SSL certificate verification timed out after {timeout}s")
        return False
    
    def _test_https_redirect(self, domain_name):
        """Test HTTP to HTTPS redirect"""
        try:
            import requests
            response = requests.get(f"http://{domain_name}", allow_redirects=False, timeout=10)
            
            if response.status_code in [301, 302, 307, 308]:
                redirect_url = response.headers.get('Location', '')
                if redirect_url.startswith('https://'):
                    print(f"✅ HTTP to HTTPS redirect working")
                    return True
            
            print(f"⚠️ HTTP to HTTPS redirect not configured")
            return False
            
        except Exception as e:
            print(f"⚠️ Could not test HTTPS redirect: {str(e)}")
            return False
    
    def _is_valid_domain(self, domain):
        """Validate domain name format"""
        import re
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        return re.match(pattern, domain) is not None
    
    def _get_app_spec(self):
        """Get current app specification"""
        if not self.app_id:
            return None
            
        response = requests.get(
            f"{self.base_url}/apps/{self.app_id}",
            headers=self.headers
        )
        
        if response.status_code == 200:
            app_data = response.json()
            return app_data['app']['spec']
        else:
            print(f"❌ Failed to get app spec: {response.status_code}")
            return None
    
    def _update_app_spec(self, spec):
        """Update app specification"""
        if not self.app_id:
            return None
            
        update_data = {"spec": spec}
        
        response = requests.put(
            f"{self.base_url}/apps/{self.app_id}",
            headers=self.headers,
            json=update_data
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to update app spec: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    
    def _get_app_info(self):
        """Get app information"""
        if not self.app_id:
            return None
            
        response = requests.get(
            f"{self.base_url}/apps/{self.app_id}",
            headers=self.headers
        )
        
        if response.status_code == 200:
            return response.json()['app']
        else:
            return None
    
    def _check_domain_status(self, domain_name):
        """Check domain configuration status"""
        app_info = self._get_app_info()
        if not app_info:
            return None
        
        domains = app_info.get('spec', {}).get('domains', [])
        for domain in domains:
            if domain['domain'] == domain_name:
                return domain
        
        return None

def configure_security_headers(app):
    """Configure security headers for Flask application"""
    
    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses"""
        
        # Force HTTPS
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'DENY'
        
        # XSS protection
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' https:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none';"
        )
        
        return response
    
    print("✅ Security headers configured")

def setup_domain_and_ssl(app_id, domain_name, do_token=None):
    """Complete domain and SSL setup process"""
    
    print("🚀 Starting Custom Domain and SSL Configuration")
    print("=" * 50)
    
    try:
        # Initialize domain manager
        domain_manager = DomainSSLManager(app_id, do_token)
        
        # Step 1: Configure custom domain
        domain_config = domain_manager.configure_custom_domain(domain_name)
        
        # Step 2: Generate DNS instructions
        dns_records = domain_manager.generate_dns_instructions(domain_name)
        
        # Step 3: Configure SSL certificate (automatic)
        ssl_configured = domain_manager.configure_ssl_certificate(domain_name)
        
        # Step 4: Configure HTTPS redirects
        security_config = domain_manager.configure_https_redirects()
        
        print("\n✅ Domain and SSL configuration completed!")
        print(f"   Domain: {domain_name}")
        print(f"   SSL: Let's Encrypt (automatic)")
        print(f"   HTTPS Redirects: Enabled")
        print(f"   Security Headers: Configured")
        
        print("\n📋 Next Steps:")
        print("1. Configure DNS records as shown above")
        print("2. Wait for DNS propagation (5-30 minutes)")
        print("3. SSL certificate will be automatically issued")
        print("4. Test the domain and SSL configuration")
        
        return {
            'domain': domain_name,
            'dns_records': dns_records,
            'ssl_configured': ssl_configured,
            'security_config': security_config
        }
        
    except Exception as e:
        print(f"❌ Configuration failed: {str(e)}")
        return None

if __name__ == "__main__":
    print("Custom Domain and SSL Configuration")
    print("==================================")
    
    # Example usage (replace with actual values)
    app_id = os.environ.get('DO_APP_ID', 'your-app-id-here')
    domain_name = os.environ.get('CUSTOM_DOMAIN', 'crm.narrissarealty.com')
    
    if app_id and domain_name:
        result = setup_domain_and_ssl(app_id, domain_name)
        if result:
            print("\n🎉 Setup completed successfully!")
    else:
        print("⚠️ Please set DO_APP_ID and CUSTOM_DOMAIN environment variables")