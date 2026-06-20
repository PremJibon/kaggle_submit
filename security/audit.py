from typing import Any, Dict, Optional
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class AuditEvent:
    """Audit event model."""

    def __init__(self, event_type: str, user_id: str, resource: str, action: str, details: Dict[str, Any] = None):
        self.id = f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        self.event_type = event_type
        self.user_id = user_id
        self.resource = resource
        self.action = action
        self.details = details or {}
        self.timestamp = datetime.now()
        self.ip_address = None
        self.user_agent = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "event_type": self.event_type,
            "user_id": self.user_id,
            "resource": self.resource,
            "action": self.action,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
        }


class AuditLogger:
    """Audit logging service."""

    def __init__(self):
        self.events: list = []
        self.logger = logging.getLogger("audit")

    def log_event(self, event_type: str, user_id: str, resource: str, action: str, details: Dict[str, Any] = None, ip_address: str = None, user_agent: str = None) -> AuditEvent:
        """Log an audit event."""
        event = AuditEvent(
            event_type=event_type,
            user_id=user_id,
            resource=resource,
            action=action,
            details=details
        )
        
        if ip_address:
            event.ip_address = ip_address
        if user_agent:
            event.user_agent = user_agent
        
        self.events.append(event)
        self.logger.info(f"Audit event: {event_type} - {action} on {resource} by {user_id}")
        
        return event

    def log_user_action(self, user_id: str, action: str, resource: str, details: Dict[str, Any] = None) -> AuditEvent:
        """Log a user action."""
        return self.log_event(
            event_type="user_action",
            user_id=user_id,
            resource=resource,
            action=action,
            details=details
        )

    def log_security_event(self, user_id: str, action: str, resource: str, details: Dict[str, Any] = None) -> AuditEvent:
        """Log a security event."""
        return self.log_event(
            event_type="security",
            user_id=user_id,
            resource=resource,
            action=action,
            details=details
        )

    def log_data_access(self, user_id: str, resource: str, action: str, details: Dict[str, Any] = None) -> AuditEvent:
        """Log data access."""
        return self.log_event(
            event_type="data_access",
            user_id=user_id,
            resource=resource,
            action=action,
            details=details
        )

    def get_events(self, user_id: Optional[str] = None, event_type: Optional[str] = None, limit: int = 100) -> list:
        """Get audit events with optional filters."""
        filtered = self.events
        
        if user_id:
            filtered = [e for e in filtered if e.user_id == user_id]
        
        if event_type:
            filtered = [e for e in filtered if e.event_type == event_type]
        
        return [e.to_dict() for e in filtered[-limit:]]

    def get_user_activity(self, user_id: str) -> Dict[str, Any]:
        """Get activity summary for a user."""
        user_events = [e for e in self.events if e.user_id == user_id]
        
        activity_summary = {
            "user_id": user_id,
            "total_events": len(user_events),
            "event_types": {},
            "recent_events": [e.to_dict() for e in user_events[-10:]]
        }
        
        for event in user_events:
            event_type = event.event_type
            if event_type not in activity_summary["event_types"]:
                activity_summary["event_types"][event_type] = 0
            activity_summary["event_types"][event_type] += 1
        
        return activity_summary

    def export_events(self, format: str = "json") -> str:
        """Export audit events."""
        events_dict = [e.to_dict() for e in self.events]
        
        if format == "json":
            return json.dumps(events_dict, indent=2)
        else:
            # CSV format
            if not events_dict:
                return ""
            
            headers = events_dict[0].keys()
            lines = [",".join(headers)]
            
            for event in events_dict:
                values = [str(event.get(h, "")) for h in headers]
                lines.append(",".join(values))
            
            return "\n".join(lines)