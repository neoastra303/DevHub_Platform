from .models import AuditLog


def record_audit_event(*, actor, action, target, metadata=None):
    AuditLog.objects.create(
        actor=actor if getattr(actor, "is_authenticated", False) else None,
        action=action,
        target_type=target.__class__.__name__,
        target_id=str(target.pk),
        metadata=metadata or {},
    )
