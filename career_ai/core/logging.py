"""
Logging configuration for Career AI.
Ensures clean, structured logs while guarding against leaking secrets.
"""

import logging
import re
import sys
from typing import Optional

SENSITIVE_PATTERNS = [
    re.compile(r'(?i)(api[_-]?key|secret|token|authorization)\s*[:=]\s*["\']?([^"\'\s]+)["\']?')
]

class SecretRedactingFormatter(logging.Formatter):
    """Custom formatter to redact sensitive tokens and keys from log messages."""
    
    def format(self, record: logging.LogRecord) -> str:
        formatted = super().format(record)
        for pattern in SENSITIVE_PATTERNS:
            formatted = pattern.sub(r'\1: [REDACTED]', formatted)
        return formatted

def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configures the root logger with a redacting stream handler."""
    logger = logging.getLogger("career_ai")
    
    # Avoid double-adding handlers
    if not logger.handlers:
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, level.upper(), logging.INFO))
        
        formatter = SecretRedactingFormatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Returns a child logger for a specific module."""
    if name:
        return logging.getLogger(f"career_ai.{name}")
    return logging.getLogger("career_ai")
