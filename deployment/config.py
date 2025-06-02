"""
Centralized Configuration Management for Cloud Deployment
"""

import os
from datetime import timedelta
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    use_supabase: bool = True
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    sqlite_path: str = "real_estate_crm.db"
    connection_pool_size: int = 20
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        return cls(
            use_supabase=os.getenv('USE_SUPABASE', 'true').lower() == 'true',
            supabase_url=os.getenv('SUPABASE_URL', ''),
            supabase_anon_key=os.getenv('SUPABASE_ANON_KEY', ''),
            supabase_service_role_key=os.getenv('SUPABASE_SERVICE_ROLE_KEY', ''),
            sqlite_path=os.getenv('SQLITE_PATH', 'real_estate_crm.db'),
            connection_pool_size=int(os.getenv('DB_POOL_SIZE', '20'))
        )

@dataclass 
class SecurityConfig:
    """Security configuration settings"""
    session_cookie_secure: bool = True
    session_cookie_httponly: bool = True
    session_cookie_samesite: str = 'Lax'
    permanent_session_lifetime: timedelta = timedelta(hours=24)
    csrf_enabled: bool = True
    password_min_length: int = 8
    rate_limit_default: str = "200 per day, 50 per hour"
    api_key_header: str = 'X-API-Key'
    
    # Content Security Policy
    csp_default_src: list = None
    csp_script_src: list = None
    csp_style_src: list = None
    csp_img_src: list = None
    
    def __post_init__(self):
        if self.csp_default_src is None:
            self.csp_default_src = ["'self'"]
        if self.csp_script_src is None:
            self.csp_script_src = ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"]
        if self.csp_style_src is None:
            self.csp_style_src = ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"]
        if self.csp_img_src is None:
            self.csp_img_src = ["'self'", "data:", "https:"]

@dataclass
class PerformanceConfig:
    """Performance configuration settings"""
    enable_caching: bool = True
    cache_timeout: int = 300  # 5 minutes
    max_concurrent_users: int = 100
    request_timeout: int = 30
    response_time_target_ms: int = 500
    throughput_target_rps: int = 50
    
    # Load testing scenarios
    light_load_users: int = 10
    medium_load_users: int = 25
    heavy_load_users: int = 50
    ai_load_users: int = 5

@dataclass
class MonitoringConfig:
    """Monitoring and logging configuration"""
    log_level: str = 'INFO'
    log_sensitive_data: bool = False
    health_check_enabled: bool = True
    metrics_enabled: bool = True
    error_tracking_enabled: bool = True
    backup_retention_days: int = 30

@dataclass
class DeploymentConfig:
    """Main deployment configuration"""
    environment: str = 'production'
    debug: bool = False
    production_url: str = "https://real-estate-crm-rfzvf.ondigitalocean.app"
    digitalocean_app_id: str = "587e41de-80fa-4a06-b0ba-40b20313b61b"
    
    # Sub-configurations
    database: DatabaseConfig = None
    security: SecurityConfig = None
    performance: PerformanceConfig = None
    monitoring: MonitoringConfig = None
    
    def __post_init__(self):
        if self.database is None:
            self.database = DatabaseConfig.from_env()
        if self.security is None:
            self.security = SecurityConfig()
        if self.performance is None:
            self.performance = PerformanceConfig()
        if self.monitoring is None:
            self.monitoring = MonitoringConfig()
    
    @classmethod
    def from_env(cls, environment: Optional[str] = None) -> 'DeploymentConfig':
        """Create configuration from environment variables"""
        env = environment or os.getenv('FLASK_ENV', 'production')
        
        config = cls(
            environment=env,
            debug=env != 'production',
            production_url=os.getenv('PRODUCTION_URL', "https://real-estate-crm-rfzvf.ondigitalocean.app"),
            digitalocean_app_id=os.getenv('DIGITALOCEAN_APP_ID', "587e41de-80fa-4a06-b0ba-40b20313b61b")
        )
        
        return config
    
    def validate(self) -> Dict[str, Any]:
        """Validate configuration and return status"""
        issues = []
        
        # Database validation
        if self.database.use_supabase:
            if not self.database.supabase_url:
                issues.append("SUPABASE_URL not configured")
            if not self.database.supabase_anon_key:
                issues.append("SUPABASE_ANON_KEY not configured")
        
        # Security validation
        if self.environment == 'production' and not self.security.session_cookie_secure:
            issues.append("Session cookies should be secure in production")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'environment': self.environment
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'environment': self.environment,
            'debug': self.debug,
            'production_url': self.production_url,
            'database': {
                'use_supabase': self.database.use_supabase,
                'connection_pool_size': self.database.connection_pool_size
            },
            'security': {
                'csrf_enabled': self.security.csrf_enabled,
                'rate_limit_default': self.security.rate_limit_default
            },
            'performance': {
                'max_concurrent_users': self.performance.max_concurrent_users,
                'response_time_target_ms': self.performance.response_time_target_ms
            },
            'monitoring': {
                'log_level': self.monitoring.log_level,
                'health_check_enabled': self.monitoring.health_check_enabled
            }
        }


# Global configuration instance
_config: Optional[DeploymentConfig] = None

def get_config() -> DeploymentConfig:
    """Get global configuration instance"""
    global _config
    if _config is None:
        _config = DeploymentConfig.from_env()
    return _config

def set_config(config: DeploymentConfig) -> None:
    """Set global configuration instance"""
    global _config
    _config = config