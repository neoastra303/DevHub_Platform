from .models import AuditLog


def record_audit_event(*, actor, action, target, metadata=None):
    AuditLog.objects.create(
        actor=actor if getattr(actor, "is_authenticated", False) else None,
        action=action,
        content_object=target,
        metadata=metadata or {},
    )
