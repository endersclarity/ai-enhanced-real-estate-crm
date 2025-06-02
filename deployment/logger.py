"""
Standardized Logging Framework for Cloud Deployment
"""

import logging
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

class DeploymentLogger:
    """Standardized logger for deployment operations"""
    
    def __init__(self, name: str = "deployment", log_level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup console and file handlers"""
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(name)s] %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler (optional)
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(
            log_dir / f"deployment_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def info(self, message: str, **kwargs):
        """Log info message with emoji"""
        self.logger.info(f"ℹ️ {message}", extra=kwargs)
    
    def success(self, message: str, **kwargs):
        """Log success message with emoji"""
        self.logger.info(f"✅ {message}", extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with emoji"""
        self.logger.warning(f"⚠️ {message}", extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with emoji"""
        self.logger.error(f"❌ {message}", extra=kwargs)
    
    def test(self, message: str, **kwargs):
        """Log test message with emoji"""
        self.logger.info(f"🧪 {message}", extra=kwargs)
    
    def security(self, message: str, **kwargs):
        """Log security message with emoji"""
        self.logger.info(f"🔒 {message}", extra=kwargs)
    
    def performance(self, message: str, **kwargs):
        """Log performance message with emoji"""
        self.logger.info(f"⚡ {message}", extra=kwargs)
    
    def section(self, title: str, level: int = 1):
        """Log section header"""
        if level == 1:
            separator = "=" * 60
            self.logger.info(f"\n{separator}")
            self.logger.info(f"{title.upper()}")
            self.logger.info(separator)
        elif level == 2:
            self.logger.info(f"\n{'=' * 40}")
            self.logger.info(f"{title}")
            self.logger.info("=" * 40)
        else:
            self.logger.info(f"\n--- {title} ---")


class TaskLogger(DeploymentLogger):
    """Logger specifically for deployment tasks"""
    
    def __init__(self, task_id: int, task_name: str):
        super().__init__(f"task_{task_id}")
        self.task_id = task_id
        self.task_name = task_name
        self.start_time = datetime.now()
        self.steps_completed = 0
        self.total_steps = 0
    
    def start_task(self, total_steps: int = 0):
        """Start task logging"""
        self.total_steps = total_steps
        self.section(f"TASK #{self.task_id}: {self.task_name}", level=1)
        self.info(f"Starting task with {total_steps} steps")
    
    def step(self, step_name: str, step_number: Optional[int] = None):
        """Log task step"""
        if step_number is None:
            self.steps_completed += 1
            step_number = self.steps_completed
        
        progress = ""
        if self.total_steps > 0:
            progress = f" ({step_number}/{self.total_steps})"
        
        self.info(f"Step {step_number}{progress}: {step_name}")
    
    def complete_task(self, results: Optional[Dict[str, Any]] = None):
        """Complete task logging"""
        duration = datetime.now() - self.start_time
        self.success(f"Task #{self.task_id} completed in {duration}")
        
        if results:
            self.info("Task Results:")
            for key, value in results.items():
                self.info(f"  {key}: {value}")


def setup_logger(name: str = "deployment", log_level: str = "INFO") -> DeploymentLogger:
    """Setup and return a deployment logger"""
    return DeploymentLogger(name, log_level)


def setup_task_logger(task_id: int, task_name: str) -> TaskLogger:
    """Setup and return a task logger"""
    return TaskLogger(task_id, task_name)


# Global logger instance
_logger: Optional[DeploymentLogger] = None

def get_logger() -> DeploymentLogger:
    """Get global logger instance"""
    global _logger
    if _logger is None:
        _logger = setup_logger()
    return _logger