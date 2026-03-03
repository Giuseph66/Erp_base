"""
Audit Middleware for Security Logging and Monitoring
"""
import logging
import uuid
import time
from datetime import datetime
from typing import Optional, Dict, Any, Callable
from functools import wraps


class AuditMiddleware:
    """Middleware for auditing requests and security events."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("audit")
        self.request_id_header = "X-Request-ID"
        
    def generate_request_id(self) -> str:
        """Generate a unique request ID."""
        return str(uuid.uuid4())
    
    def audit_request(self, request: Any, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Audit an incoming request.
        
        Args:
            request: The HTTP request object
            user_id: Optional user identifier
            
        Returns:
            Audit record dictionary
        """
        request_id = self.generate_request_id()
        timestamp = datetime.utcnow().isoformat()
        
        audit_record = {
            "event_type": "request",
            "request_id": request_id,
            "timestamp": timestamp,
            "user_id": user_id,
            "method": getattr(request, "method", "UNKNOWN"),
            "path": getattr(request, "path", "UNKNOWN"),
            "ip_address": self._get_client_ip(request),
            "user_agent": self._get_user_agent(request),
        }
        
        self.logger.info(f"AUDIT: {audit_record}")
        return audit_record
    
    def audit_security_event(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        severity: str = "INFO"
    ) -> Dict[str, Any]:
        """
        Audit a security-related event.
        
        Args:
            event_type: Type of security event (e.g., "login_failed", "access_denied")
            user_id: Optional user identifier
            details: Additional event details
            severity: Event severity level
            
        Returns:
            Audit record dictionary
        """
        timestamp = datetime.utcnow().isoformat()
        request_id = self.generate_request_id()
        
        audit_record = {
            "event_type": event_type,
            "request_id": request_id,
            "timestamp": timestamp,
            "user_id": user_id,
            "severity": severity,
            "details": details or {},
        }
        
        log_method = getattr(self.logger, severity.lower(), self.logger.info)
        log_method(f"SECURITY_AUDIT: {audit_record}")
        
        return audit_record
    
    def _get_client_ip(self, request: Any) -> str:
        """Extract client IP from request."""
        if hasattr(request, "headers"):
            forwarded = request.headers.get("X-Forwarded-For")
            if forwarded:
                return forwarded.split(",")[0].strip()
            real_ip = request.headers.get("X-Real-IP")
            if real_ip:
                return real_ip
        return getattr(request, "remote_addr", "UNKNOWN")
    
    def _get_user_agent(self, request: Any) -> str:
        """Extract user agent from request."""
        if hasattr(request, "headers"):
            return request.headers.get("User-Agent", "UNKNOWN")
        return "UNKNOWN"
    
    def middleware(self, func: Callable) -> Callable:
        """
        Decorator to apply audit middleware to a function.
        
        Args:
            func: The function to wrap
            
        Returns:
            Wrapped function with audit logging
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            request = kwargs.get("request") or (args[0] if args else None)
            user_id = kwargs.get("user_id")
            
            self.audit_request(request, user_id)
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                self.logger.info(f"Request completed in {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                self.audit_security_event(
                    event_type="request_error",
                    details={"error": str(e), "duration": duration},
                    severity="ERROR"
                )
                raise
        
        return wrapper


# Flask-specific middleware
class FlaskAuditMiddleware:
    """Flask-specific audit middleware."""
    
    def __init__(self, app=None, logger: Optional[logging.Logger] = None):
        self.audit = AuditMiddleware(logger)
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app."""
        @app.before_request
        def before_request():
            from flask import request
            self.audit.audit_request(request)
        
        @app.after_request
        def after_request(response):
            from flask import request, g
            if not hasattr(g, 'request_id'):
                g.request_id = self.audit.generate_request_id()
            response.headers[self.audit.request_id_header] = g.request_id
            return response
