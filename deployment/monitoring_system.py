#!/usr/bin/env python3
"""
Production Monitoring and Error Tracking System for Narissa Realty CRM
Implements Sentry error tracking, performance monitoring, log aggregation, and uptime monitoring
"""

import os
import json
import time
import logging
import requests
import psutil
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, g
from threading import Thread
import subprocess
import traceback
from typing import Dict, List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SentryIntegration:
    """Sentry error tracking integration"""
    
    def __init__(self, dsn: str = None):
        self.dsn = dsn or os.getenv('SENTRY_DSN')
        self.enabled = bool(self.dsn)
        
        if self.enabled:
            try:
                import sentry_sdk
                from sentry_sdk.integrations.flask import FlaskIntegration
                from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
                
                sentry_sdk.init(
                    dsn=self.dsn,
                    integrations=[
                        FlaskIntegration(auto_enabling_integrations=False),
                        SqlalchemyIntegration()
                    ],
                    traces_sample_rate=0.1,  # 10% of transactions for performance monitoring
                    environment=os.getenv('ENVIRONMENT', 'production'),
                    release=os.getenv('APP_VERSION', '1.0.0'),
                    before_send=self.filter_errors
                )
                
                logger.info("Sentry integration initialized")
            except ImportError:
                logger.warning("Sentry SDK not installed. Error tracking disabled.")
                self.enabled = False
    
    def filter_errors(self, event, hint):
        """Filter out unwanted errors"""
        # Don't track 404 errors
        if event.get('request', {}).get('status_code') == 404:
            return None
        
        # Don't track health check errors
        if '/health' in event.get('request', {}).get('url', ''):
            return None
        
        return event
    
    def capture_exception(self, exception, extra_data=None):
        """Capture exception to Sentry"""
        if self.enabled:
            import sentry_sdk
            with sentry_sdk.configure_scope() as scope:
                if extra_data:
                    for key, value in extra_data.items():
                        scope.set_extra(key, value)
                sentry_sdk.capture_exception(exception)
    
    def capture_message(self, message, level='info', extra_data=None):
        """Capture message to Sentry"""
        if self.enabled:
            import sentry_sdk
            with sentry_sdk.configure_scope() as scope:
                if extra_data:
                    for key, value in extra_data.items():
                        scope.set_extra(key, value)
                sentry_sdk.capture_message(message, level)

class PerformanceMonitor:
    """Application performance monitoring"""
    
    def __init__(self, db_path="real_estate_crm.db"):
        self.db_path = db_path
        self.init_monitoring_tables()
        self.response_time_threshold = 1.0  # 1 second
        self.error_rate_threshold = 0.05    # 5%
    
    def init_monitoring_tables(self):
        """Initialize monitoring database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Request performance tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS request_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    method TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    user_id INTEGER,
                    ip_address TEXT,
                    user_agent TEXT,
                    response_time REAL NOT NULL,
                    status_code INTEGER NOT NULL,
                    content_length INTEGER,
                    memory_usage REAL,
                    cpu_usage REAL
                )
            ''')
            
            # System metrics tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    cpu_percent REAL,
                    memory_percent REAL,
                    memory_available REAL,
                    disk_usage REAL,
                    active_connections INTEGER,
                    response_time_avg REAL,
                    error_rate REAL
                )
            ''')
            
            # Application errors tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS application_errors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    error_type TEXT NOT NULL,
                    error_message TEXT NOT NULL,
                    stack_trace TEXT,
                    endpoint TEXT,
                    user_id INTEGER,
                    ip_address TEXT,
                    request_data TEXT,
                    severity TEXT DEFAULT 'error'
                )
            ''')
            
            # Health check results
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS health_checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    check_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    response_time REAL,
                    details TEXT,
                    error_message TEXT
                )
            ''')
            
            conn.commit()
            logger.info("Monitoring database tables initialized")
    
    def record_request_metric(self, method: str, endpoint: str, response_time: float, 
                            status_code: int, user_id: int = None, ip_address: str = None,
                            user_agent: str = None, content_length: int = None):
        """Record request performance metrics"""
        try:
            # Get current system metrics
            cpu_usage = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO request_metrics 
                    (method, endpoint, user_id, ip_address, user_agent, response_time, 
                     status_code, content_length, memory_usage, cpu_usage)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (method, endpoint, user_id, ip_address, user_agent, response_time,
                      status_code, content_length, memory_usage, cpu_usage))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to record request metric: {e}")
    
    def record_system_metrics(self):
        """Record current system metrics"""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get application metrics
            response_time_avg = self.get_average_response_time()
            error_rate = self.get_current_error_rate()
            active_connections = self.get_active_connections()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO system_metrics 
                    (cpu_percent, memory_percent, memory_available, disk_usage, 
                     active_connections, response_time_avg, error_rate)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (cpu_percent, memory.percent, memory.available / (1024**3),
                      disk.percent, active_connections, response_time_avg, error_rate))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to record system metrics: {e}")
    
    def record_application_error(self, error_type: str, error_message: str, 
                               stack_trace: str = None, endpoint: str = None,
                               user_id: int = None, ip_address: str = None,
                               request_data: str = None, severity: str = 'error'):
        """Record application error"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO application_errors 
                    (error_type, error_message, stack_trace, endpoint, user_id, 
                     ip_address, request_data, severity)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (error_type, error_message, stack_trace, endpoint, user_id,
                      ip_address, request_data, severity))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to record application error: {e}")
    
    def get_average_response_time(self, minutes: int = 5) -> float:
        """Get average response time for last N minutes"""
        try:
            cutoff_time = datetime.now() - timedelta(minutes=minutes)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                result = cursor.execute('''
                    SELECT AVG(response_time) FROM request_metrics
                    WHERE timestamp > ?
                ''', (cutoff_time,)).fetchone()
                
                return result[0] if result[0] else 0.0
        except Exception as e:
            logger.error(f"Failed to get average response time: {e}")
            return 0.0
    
    def get_current_error_rate(self, minutes: int = 5) -> float:
        """Get error rate for last N minutes"""
        try:
            cutoff_time = datetime.now() - timedelta(minutes=minutes)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                total_requests = cursor.execute('''
                    SELECT COUNT(*) FROM request_metrics
                    WHERE timestamp > ?
                ''', (cutoff_time,)).fetchone()[0]
                
                error_requests = cursor.execute('''
                    SELECT COUNT(*) FROM request_metrics
                    WHERE timestamp > ? AND status_code >= 400
                ''', (cutoff_time,)).fetchone()[0]
                
                return (error_requests / total_requests) if total_requests > 0 else 0.0
        except Exception as e:
            logger.error(f"Failed to get error rate: {e}")
            return 0.0
    
    def get_active_connections(self) -> int:
        """Get number of active network connections"""
        try:
            connections = psutil.net_connections(kind='tcp')
            return len([conn for conn in connections if conn.status == 'ESTABLISHED'])
        except Exception as e:
            logger.error(f"Failed to get active connections: {e}")
            return 0

class LogAggregator:
    """Log aggregation and analysis system"""
    
    def __init__(self, db_path="real_estate_crm.db"):
        self.db_path = db_path
        self.init_log_tables()
    
    def init_log_tables(self):
        """Initialize log storage tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS application_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    level TEXT NOT NULL,
                    logger_name TEXT,
                    message TEXT NOT NULL,
                    module TEXT,
                    function_name TEXT,
                    line_number INTEGER,
                    user_id INTEGER,
                    session_id TEXT,
                    request_id TEXT
                )
            ''')
            
            conn.commit()
    
    def log_message(self, level: str, message: str, logger_name: str = None,
                   module: str = None, function_name: str = None, line_number: int = None,
                   user_id: int = None, session_id: str = None, request_id: str = None):
        """Store log message in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO application_logs 
                    (level, logger_name, message, module, function_name, line_number,
                     user_id, session_id, request_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (level, logger_name, message, module, function_name, line_number,
                      user_id, session_id, request_id))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to store log message: {e}")
    
    def get_recent_logs(self, hours: int = 24, level: str = None) -> List[Dict]:
        """Get recent log entries"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT timestamp, level, logger_name, message, module, user_id
                FROM application_logs
                WHERE timestamp > ?
            '''
            params = [cutoff_time]
            
            if level:
                query += ' AND level = ?'
                params.append(level)
            
            query += ' ORDER BY timestamp DESC LIMIT 1000'
            
            logs = cursor.execute(query, params).fetchall()
            
            return [
                {
                    'timestamp': log[0],
                    'level': log[1],
                    'logger_name': log[2],
                    'message': log[3],
                    'module': log[4],
                    'user_id': log[5]
                }
                for log in logs
            ]

class UptimeMonitor:
    """Uptime and health check monitoring"""
    
    def __init__(self, db_path="real_estate_crm.db"):
        self.db_path = db_path
        self.performance_monitor = PerformanceMonitor(db_path)
        self.endpoints_to_monitor = [
            '/health',
            '/api/users',
            '/api/clients',
            '/auth/profile'
        ]
    
    def perform_health_check(self, endpoint: str, base_url: str = "http://localhost:8000") -> Dict:
        """Perform health check on endpoint"""
        start_time = time.time()
        
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            response_time = time.time() - start_time
            
            status = "healthy" if response.status_code < 400 else "unhealthy"
            
            check_result = {
                'endpoint': endpoint,
                'status': status,
                'response_time': response_time,
                'status_code': response.status_code,
                'timestamp': datetime.now().isoformat()
            }
            
            # Record in database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO health_checks (check_type, status, response_time, details)
                    VALUES (?, ?, ?, ?)
                ''', (f"endpoint_{endpoint}", status, response_time, json.dumps(check_result)))
                conn.commit()
            
            return check_result
            
        except Exception as e:
            response_time = time.time() - start_time
            
            error_result = {
                'endpoint': endpoint,
                'status': 'error',
                'response_time': response_time,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
            # Record error in database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO health_checks (check_type, status, response_time, error_message)
                    VALUES (?, ?, ?, ?)
                ''', (f"endpoint_{endpoint}", 'error', response_time, str(e)))
                conn.commit()
            
            return error_result
    
    def perform_system_health_check(self) -> Dict:
        """Perform comprehensive system health check"""
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'checks': {}
        }
        
        # Check CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        health_status['checks']['cpu'] = {
            'status': 'healthy' if cpu_percent < 80 else 'warning' if cpu_percent < 95 else 'critical',
            'value': cpu_percent,
            'unit': 'percent'
        }
        
        # Check memory usage
        memory = psutil.virtual_memory()
        health_status['checks']['memory'] = {
            'status': 'healthy' if memory.percent < 80 else 'warning' if memory.percent < 95 else 'critical',
            'value': memory.percent,
            'unit': 'percent',
            'available_gb': memory.available / (1024**3)
        }
        
        # Check disk usage
        disk = psutil.disk_usage('/')
        health_status['checks']['disk'] = {
            'status': 'healthy' if disk.percent < 80 else 'warning' if disk.percent < 95 else 'critical',
            'value': disk.percent,
            'unit': 'percent'
        }
        
        # Check database connectivity
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1').fetchone()
            health_status['checks']['database'] = {
                'status': 'healthy',
                'message': 'Database connection successful'
            }
        except Exception as e:
            health_status['checks']['database'] = {
                'status': 'critical',
                'error': str(e)
            }
            health_status['overall_status'] = 'unhealthy'
        
        # Check application performance
        avg_response_time = self.performance_monitor.get_average_response_time()
        error_rate = self.performance_monitor.get_current_error_rate()
        
        health_status['checks']['performance'] = {
            'avg_response_time': avg_response_time,
            'error_rate': error_rate,
            'status': 'healthy' if avg_response_time < 1.0 and error_rate < 0.05 else 'warning'
        }
        
        # Determine overall status
        critical_checks = [check for check in health_status['checks'].values() 
                          if check.get('status') == 'critical']
        if critical_checks:
            health_status['overall_status'] = 'critical'
        elif any(check.get('status') == 'warning' for check in health_status['checks'].values()):
            health_status['overall_status'] = 'warning'
        
        # Record in database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO health_checks (check_type, status, details)
                VALUES (?, ?, ?)
            ''', ('system_health', health_status['overall_status'], json.dumps(health_status)))
            conn.commit()
        
        return health_status

class AlertSystem:
    """Alert and notification system"""
    
    def __init__(self, config: Dict = None):
        self.config = config or self.get_default_config()
        self.alert_history = []
    
    def get_default_config(self) -> Dict:
        """Get default alert configuration"""
        return {
            'email': {
                'enabled': bool(os.getenv('SMTP_SERVER')),
                'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
                'smtp_port': int(os.getenv('SMTP_PORT', 587)),
                'username': os.getenv('SMTP_USERNAME', ''),
                'password': os.getenv('SMTP_PASSWORD', ''),
                'from_email': os.getenv('ALERT_FROM_EMAIL', 'alerts@narissarealty.com'),
                'to_emails': os.getenv('ALERT_TO_EMAILS', 'admin@narissarealty.com').split(',')
            },
            'thresholds': {
                'cpu_critical': 95,
                'memory_critical': 95,
                'disk_critical': 95,
                'response_time_warning': 1.0,
                'response_time_critical': 5.0,
                'error_rate_warning': 0.05,
                'error_rate_critical': 0.15
            }
        }
    
    def send_email_alert(self, subject: str, message: str, severity: str = 'warning'):
        """Send email alert"""
        if not self.config['email']['enabled']:
            logger.warning("Email alerts not configured")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['email']['from_email']
            msg['To'] = ', '.join(self.config['email']['to_emails'])
            msg['Subject'] = f"[{severity.upper()}] CRM Alert: {subject}"
            
            body = f"""
Alert Details:
Severity: {severity.upper()}
Time: {datetime.now().isoformat()}
Subject: {subject}

Message:
{message}

--
Narissa Realty CRM Monitoring System
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.config['email']['smtp_server'], self.config['email']['smtp_port'])
            server.starttls()
            server.login(self.config['email']['username'], self.config['email']['password'])
            text = msg.as_string()
            server.sendmail(self.config['email']['from_email'], self.config['email']['to_emails'], text)
            server.quit()
            
            logger.info(f"Alert email sent: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False
    
    def check_and_alert(self, health_status: Dict):
        """Check health status and send alerts if needed"""
        alerts_to_send = []
        
        # Check CPU
        cpu_check = health_status['checks'].get('cpu', {})
        if cpu_check.get('status') == 'critical':
            alerts_to_send.append({
                'subject': 'High CPU Usage',
                'message': f"CPU usage is at {cpu_check['value']}%",
                'severity': 'critical'
            })
        
        # Check Memory
        memory_check = health_status['checks'].get('memory', {})
        if memory_check.get('status') == 'critical':
            alerts_to_send.append({
                'subject': 'High Memory Usage',
                'message': f"Memory usage is at {memory_check['value']}%",
                'severity': 'critical'
            })
        
        # Check Disk
        disk_check = health_status['checks'].get('disk', {})
        if disk_check.get('status') == 'critical':
            alerts_to_send.append({
                'subject': 'High Disk Usage',
                'message': f"Disk usage is at {disk_check['value']}%",
                'severity': 'critical'
            })
        
        # Check Performance
        perf_check = health_status['checks'].get('performance', {})
        if perf_check.get('avg_response_time', 0) > self.config['thresholds']['response_time_critical']:
            alerts_to_send.append({
                'subject': 'Poor Application Performance',
                'message': f"Average response time is {perf_check['avg_response_time']:.2f}s",
                'severity': 'critical'
            })
        
        # Send alerts
        for alert in alerts_to_send:
            # Avoid duplicate alerts within 30 minutes
            recent_alert = any(
                a['subject'] == alert['subject'] and 
                datetime.now() - a['timestamp'] < timedelta(minutes=30)
                for a in self.alert_history
            )
            
            if not recent_alert:
                if self.send_email_alert(alert['subject'], alert['message'], alert['severity']):
                    self.alert_history.append({
                        'timestamp': datetime.now(),
                        'subject': alert['subject'],
                        'severity': alert['severity']
                    })

class MonitoringSystem:
    """Comprehensive monitoring system"""
    
    def __init__(self, db_path="real_estate_crm.db"):
        self.db_path = db_path
        self.sentry = SentryIntegration()
        self.performance_monitor = PerformanceMonitor(db_path)
        self.log_aggregator = LogAggregator(db_path)
        self.uptime_monitor = UptimeMonitor(db_path)
        self.alert_system = AlertSystem()
        self.monitoring_active = False
    
    def start_monitoring(self):
        """Start background monitoring processes"""
        self.monitoring_active = True
        
        # Start system metrics collection
        metrics_thread = Thread(target=self._collect_system_metrics, daemon=True)
        metrics_thread.start()
        
        # Start health checks
        health_thread = Thread(target=self._perform_health_checks, daemon=True)
        health_thread.start()
        
        logger.info("Monitoring system started")
    
    def stop_monitoring(self):
        """Stop monitoring processes"""
        self.monitoring_active = False
        logger.info("Monitoring system stopped")
    
    def _collect_system_metrics(self):
        """Background system metrics collection"""
        while self.monitoring_active:
            try:
                self.performance_monitor.record_system_metrics()
                time.sleep(60)  # Collect metrics every minute
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
                time.sleep(60)
    
    def _perform_health_checks(self):
        """Background health checks"""
        while self.monitoring_active:
            try:
                # Perform system health check
                health_status = self.uptime_monitor.perform_system_health_check()
                
                # Check for alerts
                self.alert_system.check_and_alert(health_status)
                
                time.sleep(300)  # Health checks every 5 minutes
            except Exception as e:
                logger.error(f"Error performing health checks: {e}")
                time.sleep(300)
    
    def get_monitoring_dashboard_data(self) -> Dict:
        """Get data for monitoring dashboard"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get recent system metrics
            recent_metrics = cursor.execute('''
                SELECT timestamp, cpu_percent, memory_percent, disk_usage, 
                       active_connections, response_time_avg, error_rate
                FROM system_metrics
                WHERE timestamp > datetime('now', '-24 hours')
                ORDER BY timestamp DESC
                LIMIT 288  -- 24 hours of 5-minute intervals
            ''').fetchall()
            
            # Get recent errors
            recent_errors = cursor.execute('''
                SELECT timestamp, error_type, error_message, severity, endpoint
                FROM application_errors
                WHERE timestamp > datetime('now', '-24 hours')
                ORDER BY timestamp DESC
                LIMIT 100
            ''').fetchall()
            
            # Get recent health checks
            recent_health = cursor.execute('''
                SELECT timestamp, check_type, status, response_time
                FROM health_checks
                WHERE timestamp > datetime('now', '-24 hours')
                ORDER BY timestamp DESC
                LIMIT 100
            ''').fetchall()
            
            return {
                'system_metrics': [
                    {
                        'timestamp': metric[0],
                        'cpu_percent': metric[1],
                        'memory_percent': metric[2],
                        'disk_usage': metric[3],
                        'active_connections': metric[4],
                        'response_time_avg': metric[5],
                        'error_rate': metric[6]
                    }
                    for metric in recent_metrics
                ],
                'recent_errors': [
                    {
                        'timestamp': error[0],
                        'error_type': error[1],
                        'error_message': error[2],
                        'severity': error[3],
                        'endpoint': error[4]
                    }
                    for error in recent_errors
                ],
                'health_checks': [
                    {
                        'timestamp': check[0],
                        'check_type': check[1],
                        'status': check[2],
                        'response_time': check[3]
                    }
                    for check in recent_health
                ]
            }

def register_monitoring_routes(app: Flask, monitoring: MonitoringSystem):
    """Register monitoring routes with Flask app"""
    
    @app.before_request
    def before_request():
        """Record request start time"""
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        """Record request metrics"""
        if hasattr(g, 'start_time'):
            response_time = time.time() - g.start_time
            
            # Skip monitoring for monitoring endpoints
            if not request.endpoint or 'monitoring' in request.endpoint:
                return response
            
            try:
                from flask_login import current_user
                user_id = current_user.id if current_user.is_authenticated else None
            except:
                user_id = None
            
            monitoring.performance_monitor.record_request_metric(
                method=request.method,
                endpoint=request.endpoint or request.path,
                response_time=response_time,
                status_code=response.status_code,
                user_id=user_id,
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string,
                content_length=response.content_length
            )
        
        return response
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle and record application errors"""
        try:
            from flask_login import current_user
            user_id = current_user.id if current_user.is_authenticated else None
        except:
            user_id = None
        
        # Record error in monitoring system
        monitoring.performance_monitor.record_application_error(
            error_type=type(error).__name__,
            error_message=str(error),
            stack_trace=traceback.format_exc(),
            endpoint=request.endpoint or request.path,
            user_id=user_id,
            ip_address=request.remote_addr,
            request_data=json.dumps(request.get_json()) if request.is_json else None
        )
        
        # Send to Sentry
        monitoring.sentry.capture_exception(error, {
            'endpoint': request.endpoint,
            'user_id': user_id,
            'ip_address': request.remote_addr
        })
        
        # Return error response
        if isinstance(error, Exception):
            return jsonify({'error': 'Internal server error'}), 500
        return error
    
    @app.route('/health')
    def health_check():
        """Application health check endpoint"""
        health_status = monitoring.uptime_monitor.perform_system_health_check()
        return jsonify(health_status), 200 if health_status['overall_status'] != 'critical' else 503
    
    @app.route('/api/monitoring/dashboard')
    def monitoring_dashboard():
        """Monitoring dashboard data"""
        data = monitoring.get_monitoring_dashboard_data()
        return jsonify(data)
    
    @app.route('/api/monitoring/metrics')
    def current_metrics():
        """Current system metrics"""
        health_status = monitoring.uptime_monitor.perform_system_health_check()
        return jsonify(health_status)

def main():
    """Test the monitoring system"""
    from flask import Flask
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    # Initialize monitoring system
    monitoring = MonitoringSystem()
    
    # Register routes
    register_monitoring_routes(app, monitoring)
    
    # Start monitoring
    monitoring.start_monitoring()
    
    @app.route('/')
    def index():
        return jsonify({'message': 'CRM Monitoring System', 'status': 'running'})
    
    @app.route('/test-error')
    def test_error():
        raise Exception("Test error for monitoring")
    
    print("Monitoring system test server starting...")
    print("Visit http://localhost:5002/health for health check")
    print("Visit http://localhost:5002/api/monitoring/dashboard for dashboard")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5002)
    finally:
        monitoring.stop_monitoring()

if __name__ == "__main__":
    main()