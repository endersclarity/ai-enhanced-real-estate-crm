#!/usr/bin/env python3
"""
Quick Fix for Monitoring Integration
Simple, robust monitoring that won't break the app
"""

from flask import Flask, request, g, jsonify
import time
import psutil
from datetime import datetime
import os

def add_basic_monitoring(app):
    """Add basic monitoring without complex dependencies"""
    
    # Simple metrics tracking
    metrics = {
        'requests': 0,
        'errors': 0,
        'start_time': datetime.utcnow()
    }
    
    @app.before_request
    def before_request():
        g.start_time = time.time()
        metrics['requests'] += 1
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            
            # Count errors
            if response.status_code >= 400:
                metrics['errors'] += 1
            
            # Add response time header
            response.headers['X-Response-Time'] = f"{duration:.3f}s"
        
        return response
    
    @app.route('/health')
    def health():
        """Simple health check"""
        return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}
    
    @app.route('/health/detailed')
    def health_detailed():
        """Detailed health check"""
        try:
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            
            return {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'system': {
                    'cpu_percent': cpu,
                    'memory_percent': memory.percent,
                    'memory_available_gb': round(memory.available / (1024**3), 2)
                }
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}, 500
    
    @app.route('/metrics')
    def get_metrics():
        """Application metrics"""
        uptime = (datetime.utcnow() - metrics['start_time']).total_seconds()
        
        return {
            'uptime_seconds': uptime,
            'total_requests': metrics['requests'],
            'total_errors': metrics['errors'],
            'error_rate': (metrics['errors'] / max(metrics['requests'], 1)) * 100
        }

def add_security_headers(app):
    """Add security headers"""
    
    @app.after_request
    def security_headers(response):
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

if __name__ == "__main__":
    print("Quick monitoring fix ready for integration")