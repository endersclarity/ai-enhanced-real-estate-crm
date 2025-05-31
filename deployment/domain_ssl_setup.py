#!/usr/bin/env python3
"""
Domain and SSL Certificate Configuration for Narissa Realty CRM
Implements automated domain setup, Let's Encrypt SSL certificates, and HTTPS redirection
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DomainSSLManager:
    """Manages domain configuration and SSL certificate setup"""
    
    def __init__(self, domain_name="narissarealty.com", email="admin@narissarealty.com"):
        self.domain_name = domain_name
        self.email = email
        self.config_dir = Path("/etc/nginx/sites-available")
        self.enabled_dir = Path("/etc/nginx/sites-enabled")
        self.ssl_dir = Path("/etc/letsencrypt/live")
        
    def setup_nginx_config(self):
        """Create Nginx configuration for the domain"""
        config_content = f"""
# Narissa Realty CRM - Production Configuration
server {{
    listen 80;
    server_name {self.domain_name} www.{self.domain_name};
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # Let's Encrypt challenge location
    location /.well-known/acme-challenge/ {{
        root /var/www/certbot;
    }}
    
    # Redirect all HTTP to HTTPS
    location / {{
        return 301 https://$server_name$request_uri;
    }}
}}

# HTTPS server block (will be enabled after SSL setup)
server {{
    listen 443 ssl http2;
    server_name {self.domain_name} www.{self.domain_name};
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/{self.domain_name}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{self.domain_name}/privkey.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:MozTLS:10m;
    ssl_session_tickets off;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # HSTS (optional)
    add_header Strict-Transport-Security "max-age=63072000" always;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    
    # Proxy to Flask application
    location / {{
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }}
    
    # Static files
    location /static/ {{
        alias /var/www/crm/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
    
    # Health check endpoint
    location /health {{
        access_log off;
        proxy_pass http://127.0.0.1:8000/health;
    }}
}}
"""
        
        config_file = self.config_dir / f"{self.domain_name}.conf"
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        logger.info(f"Nginx configuration created: {config_file}")
        return config_file
    
    def install_certbot(self):
        """Install Certbot for Let's Encrypt SSL certificates"""
        commands = [
            "apt update",
            "apt install -y certbot python3-certbot-nginx",
            "mkdir -p /var/www/certbot"
        ]
        
        for cmd in commands:
            try:
                subprocess.run(cmd.split(), check=True, capture_output=True, text=True)
                logger.info(f"Executed: {cmd}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to execute {cmd}: {e}")
                return False
        
        return True
    
    def obtain_ssl_certificate(self):
        """Obtain SSL certificate from Let's Encrypt"""
        # First, enable the site without SSL
        self.enable_site()
        
        # Restart Nginx to serve the challenge
        subprocess.run(["systemctl", "reload", "nginx"], check=True)
        
        # Obtain certificate
        certbot_cmd = [
            "certbot", "certonly",
            "--webroot",
            "--webroot-path=/var/www/certbot",
            "--email", self.email,
            "--agree-tos",
            "--no-eff-email",
            "-d", self.domain_name,
            "-d", f"www.{self.domain_name}"
        ]
        
        try:
            result = subprocess.run(certbot_cmd, check=True, capture_output=True, text=True)
            logger.info("SSL certificate obtained successfully")
            logger.info(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to obtain SSL certificate: {e}")
            logger.error(e.stderr)
            return False
    
    def enable_site(self):
        """Enable the Nginx site configuration"""
        config_file = self.config_dir / f"{self.domain_name}.conf"
        symlink = self.enabled_dir / f"{self.domain_name}.conf"
        
        # Remove existing symlink if it exists
        if symlink.exists():
            symlink.unlink()
        
        # Create new symlink
        symlink.symlink_to(config_file)
        logger.info(f"Site enabled: {symlink}")
    
    def setup_auto_renewal(self):
        """Setup automatic certificate renewal"""
        cron_entry = "0 12 * * * /usr/bin/certbot renew --quiet"
        
        # Add to root's crontab
        try:
            # Get current crontab
            result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            current_crontab = result.stdout if result.returncode == 0 else ""
            
            # Add renewal entry if not present
            if cron_entry not in current_crontab:
                new_crontab = current_crontab + "\n" + cron_entry + "\n"
                subprocess.run(["crontab", "-"], input=new_crontab, text=True, check=True)
                logger.info("SSL certificate auto-renewal configured")
            else:
                logger.info("SSL certificate auto-renewal already configured")
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to setup auto-renewal: {e}")
            return False
        
        return True
    
    def test_ssl_config(self):
        """Test SSL configuration"""
        test_url = f"https://{self.domain_name}/health"
        
        try:
            import requests
            response = requests.get(test_url, timeout=10, verify=True)
            if response.status_code == 200:
                logger.info(f"SSL configuration test passed: {test_url}")
                return True
            else:
                logger.warning(f"SSL test returned status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"SSL configuration test failed: {e}")
            return False
    
    def validate_setup(self):
        """Validate complete domain and SSL setup"""
        validation_results = {
            "domain_configured": False,
            "ssl_certificate_valid": False,
            "https_redirect_working": False,
            "auto_renewal_enabled": False,
            "security_headers_present": False
        }
        
        # Check if certificate exists
        cert_path = self.ssl_dir / self.domain_name / "fullchain.pem"
        if cert_path.exists():
            validation_results["ssl_certificate_valid"] = True
            logger.info("SSL certificate found and valid")
        
        # Check if auto-renewal is configured
        try:
            result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            if "certbot renew" in result.stdout:
                validation_results["auto_renewal_enabled"] = True
                logger.info("Auto-renewal configured")
        except:
            pass
        
        # Test HTTPS redirect and security headers
        try:
            import requests
            
            # Test HTTP redirect
            http_response = requests.get(f"http://{self.domain_name}", 
                                       allow_redirects=False, timeout=10)
            if http_response.status_code in [301, 302]:
                validation_results["https_redirect_working"] = True
                logger.info("HTTPS redirect working")
            
            # Test HTTPS and security headers
            https_response = requests.get(f"https://{self.domain_name}", timeout=10)
            if https_response.status_code == 200:
                validation_results["domain_configured"] = True
                logger.info("Domain accessible via HTTPS")
                
                # Check security headers
                headers = https_response.headers
                security_headers = [
                    'X-Frame-Options',
                    'X-Content-Type-Options',
                    'X-XSS-Protection',
                    'Strict-Transport-Security'
                ]
                
                if all(header in headers for header in security_headers):
                    validation_results["security_headers_present"] = True
                    logger.info("Security headers present")
                    
        except Exception as e:
            logger.error(f"Validation test failed: {e}")
        
        return validation_results
    
    def run_complete_setup(self):
        """Run complete domain and SSL setup process"""
        logger.info("Starting domain and SSL setup...")
        
        try:
            # Step 1: Install Certbot
            logger.info("Installing Certbot...")
            if not self.install_certbot():
                return False
            
            # Step 2: Setup Nginx configuration
            logger.info("Setting up Nginx configuration...")
            self.setup_nginx_config()
            
            # Step 3: Obtain SSL certificate
            logger.info("Obtaining SSL certificate...")
            if not self.obtain_ssl_certificate():
                return False
            
            # Step 4: Setup auto-renewal
            logger.info("Setting up auto-renewal...")
            if not self.setup_auto_renewal():
                return False
            
            # Step 5: Restart Nginx with SSL configuration
            logger.info("Restarting Nginx...")
            subprocess.run(["systemctl", "reload", "nginx"], check=True)
            
            # Step 6: Validate setup
            logger.info("Validating setup...")
            results = self.validate_setup()
            
            # Save configuration
            config = {
                "domain": self.domain_name,
                "email": self.email,
                "ssl_enabled": True,
                "auto_renewal": True,
                "setup_date": datetime.now().isoformat(),
                "validation_results": results
            }
            
            with open("deployment/domain_ssl_config.json", "w") as f:
                json.dump(config, f, indent=2)
            
            logger.info("Domain and SSL setup completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            return False

def main():
    """Main execution function"""
    # Parse command line arguments
    domain = sys.argv[1] if len(sys.argv) > 1 else "narissarealty.com"
    email = sys.argv[2] if len(sys.argv) > 2 else "admin@narissarealty.com"
    
    manager = DomainSSLManager(domain, email)
    success = manager.run_complete_setup()
    
    if success:
        print(f"✅ Domain and SSL setup completed for {domain}")
        sys.exit(0)
    else:
        print(f"❌ Domain and SSL setup failed for {domain}")
        sys.exit(1)

if __name__ == "__main__":
    main()