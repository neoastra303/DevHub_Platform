import csv
import io

from django.utils import timezone

from .models import AuditLog, BackgroundJob


def enqueue_audit_export_job(*, user, filters=None):
    return BackgroundJob.objects.create(
        requested_by=user,
        job_type=BackgroundJob.JobType.AUDIT_EXPORT,
        payload={"filters": filters or {}, "requested_at": timezone.now().isoformat()},
    )


def process_background_job(job):
    if job.status != BackgroundJob.Status.QUEUED:
        return job

    job.status = BackgroundJob.Status.RUNNING
    job.error_message = ""
    job.save(update_fields=["status", "error_message", "updated_at"])

    try:
        if job.job_type == BackgroundJob.JobType.AUDIT_EXPORT:
            _process_audit_export(job)
        else:
            raise ValueError(f"Unsupported job type '{job.job_type}'")
        job.status = BackgroundJob.Status.SUCCEEDED
        job.save(update_fields=["status", "result", "updated_at"])
    except Exception as exc:
        job.status = BackgroundJob.Status.FAILED
        job.error_message = str(exc)
        job.save(update_fields=["status", "error_message", "updated_at"])
        raise

    return job


def _process_audit_export(job):
    filters = (job.payload or {}).get("filters", {})
    logs = AuditLog.objects.filter(actor=job.requested_by)
    action = filters.get("action")
    target_type = filters.get("target_type")
    if action:
        logs = logs.filter(action=action)
    if target_type:
        logs = logs.filter(target_type=target_type)

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "action", "target_type", "target_id", "created_at", "metadata"])
    for log in logs.order_by("-created_at"):
        writer.writerow([log.id, log.action, log.target_type, log.target_id, log.created_at.isoformat(), log.metadata])

    job.result = {
        "content_type": "text/csv",
        "filename": f"audit-export-{job.pk}.csv",
        "content": buffer.getvalue(),
        "row_count": logs.count(),
    }
